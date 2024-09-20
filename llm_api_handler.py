import os
import json
import time
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import anthropic
from typing import List, Dict, Any, Union, Type, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

openai_client = OpenAI(api_key=openai_api_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

T = TypeVar('T', bound=BaseModel)

class BatchResult(BaseModel, Generic[T]):
    metadata: Dict[str, Any]
    results: List[Dict[str, Union[str, T]]]

class LLMAPIHandler:
    """
    Handles interactions with OpenAI and Anthropic models for processing prompts in regular, batch, and async modes.
    """

    def __init__(self):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        # Initialize a ThreadPoolExecutor for async operations
        self.executor = ThreadPoolExecutor(max_workers=100)  # Adjust based on your requirements

    async def process(
        self, 
        prompts: Union[str, List[str]],
        model: str = "gpt-4o-mini",
        system_message: str = None,
        temperature: float = 0.7,
        mode: str = "regular",
        response_format: Union[None, Type[T]] = None,
        output_dir: str = None,
        update_interval: int = 60,
        deduplicate_prompts: bool = False
    ) -> Union[Any, T, BatchResult[T]]:
        """
        Process a prompt or list of prompts using the specified model in regular, batch, or async mode.
        Now an async method.
        """
        if mode == "async":
            if not isinstance(prompts, list):
                raise ValueError("For 'async' mode, 'prompts' should be a list of strings.")
            return await self._process_async(prompts, model, system_message, temperature, response_format)
        
        if isinstance(prompts, str):
            # Single prompt: Regular mode
            request = {
                "model": model,
                "prompt": prompts,
                "system_message": system_message,
                "temperature": temperature
            }
            return self._process_regular(request, response_format)
        
        elif isinstance(prompts, list) and mode == "batch":
            # Multiple prompts: Batch mode
            if deduplicate_prompts:
                prompts = list(dict.fromkeys(prompts))  # Remove duplicates, but keep order
            batch_requests = self._construct_batch_requests(prompts, model, temperature)
            return self._process_batch(batch_requests, response_format, output_dir, update_interval, prompts)
        else:
            raise ValueError("Invalid input: 'prompts' should be a string for regular mode or a list for batch/async mode.")

    async def _process_async(
        self, 
        prompts: List[str], 
        model: str, 
        system_message: str, 
        temperature: float, 
        response_format: Union[None, Type[T]]
    ) -> List[Union[str, T]]:
        """
        Asynchronously process a list of prompts using the specified OpenAI model.
        """
        semaphore = asyncio.Semaphore(100)  # Limit concurrent tasks based on RPM (e.g., 5000 RPM ~ 83 RPS)

        async def process_prompt(prompt: str) -> Union[str, T]:
            async with semaphore:
                return await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._process_single_prompt,
                    prompt,
                    model,
                    system_message,
                    temperature,
                    response_format
                )

        tasks = [process_prompt(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions and log errors
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing prompt '{prompts[idx]}': {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        return processed_results

    def _process_single_prompt(
        self, 
        prompt: str, 
        model: str, 
        system_message: str, 
        temperature: float, 
        response_format: Union[None, Type[T]]
    ) -> Union[str, T]:
        """
        Synchronously process a single prompt. Used by the async mode.
        """
        request = {
            "model": model,
            "prompt": prompt,
            "system_message": system_message,
            "temperature": temperature
        }
        return self._process_regular(request, response_format)

    def _construct_batch_requests(self, prompts: List[str], model: str, temperature: float) -> List[Dict[str, Any]]:
        """
        Construct a list of batch requests with the prompts, including unique custom IDs.
        """
        batch_requests = []
        for i, prompt in enumerate(prompts):
            batch_requests.append({
                "custom_id": f"request_{i+1}",  # Adding a unique custom_id for each request
                "model": model,
                "prompt": prompt,
                "temperature": temperature
            })
        return batch_requests

    def _get_system_message(self, user_system_message: str, response_format: Union[None, Type[T]]) -> str:
        """Determine the system message, handling user input and format requirements."""
        if response_format:
            schema = response_format.schema_json()
            return f"Answer exclusively in this JSON format: {schema}"
        elif user_system_message:
            return user_system_message
        else:
            return "You are a helpful assistant."

    def _process_regular(self, request: Dict[str, Any], response_format: Union[None, Type[T]]) -> Union[str, T]:
        """Process a regular request with a single prompt."""
        model = request['model']
        temperature = request.get('temperature', 0.7)
        prompt = request['prompt']
        system_message = self._get_system_message(request.get('system_message'), response_format)

        if model in ['gpt-4o-mini', 'gpt-4o-2024-08-06']:
            messages = [{"role": "user", "content": prompt}]
            if system_message:
                messages.insert(0, {"role": "system", "content": system_message})

            if response_format:
                completion = self.openai_client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=response_format
                )
                return completion.choices[0].message.parsed
            else:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                ).choices[0].message.content

        elif model == 'claude-3-5-sonnet-20240620':
            if response_format:
                schema = response_format.model_json_schema()
                prompt = f"Answer exclusively in this JSON format: {schema}\n\n{prompt}"

            message = self.anthropic_client.messages.create(
                model=model,
                max_tokens=8192,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            content = message.content[0].text

            if response_format:
                try:
                    json_response = json.loads(content)
                    return response_format(**json_response)
                except json.JSONDecodeError:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        json_response = json.loads(json_str)
                        return response_format(**json_response)
                    else:
                        raise ValueError("Failed to extract JSON from Claude's response")
            else:
                return content
        else:
            raise ValueError(f"Invalid model: {model}")

    def _process_batch(
        self, 
        requests: List[Dict[str, Any]], 
        response_format: Union[None, Type[T]], 
        output_dir: str, 
        update_interval: int, 
        original_prompts: List[str]
    ) -> BatchResult[T]:
        """Process a batch of requests and return a list of dictionaries matching prompt and response."""
        os.makedirs(output_dir, exist_ok=True)

        batch_file_path = os.path.join(output_dir, 'batch_input.jsonl')
        with open(batch_file_path, 'w') as f:
            for request in requests:
                messages = [{"role": "user", "content": request['prompt']}]
                if 'system_message' in request:
                    messages.insert(0, {"role": "system", "content": request['system_message']})
                
                if response_format:
                    schema = response_format.model_json_schema()
                    messages.insert(0, {"role": "system", "content": f"Answer exclusively in this JSON format: {schema}"})
                
                f.write(json.dumps({
                    "custom_id": request['custom_id'],
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": request['model'],
                        "messages": messages,
                        "temperature": request.get('temperature', 0.7),
                        "response_format": {"type": "json_object"}
                    }
                }) + '\n')

        with open(batch_file_path, 'rb') as f:
            batch_file = self.openai_client.files.create(file=f, purpose="batch")
        
        batch = self.openai_client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        job_metadata = {
            "batch_id": batch.id,
            "input_file_id": batch.input_file_id,
            "status": batch.status,
            "created_at": batch.created_at,
            "last_updated": datetime.now().isoformat(),
            "num_requests": len(requests)
        }

        metadata_file_path = os.path.join(output_dir, f"batch_{batch.id}_metadata.json")
        with open(metadata_file_path, 'w') as f:
            json.dump(job_metadata, f, indent=2)

        start_time = time.time()
        while True:
            current_time = time.time()
            if current_time - start_time >= update_interval:
                batch = self.openai_client.batches.retrieve(batch.id)
                job_metadata.update({
                    "status": batch.status,
                    "last_updated": datetime.now().isoformat()
                })
                with open(metadata_file_path, 'w') as f:
                    json.dump(job_metadata, f, indent=2)
                logger.info(f"Batch status: {batch.status}")
                start_time = current_time

            if batch.status == "completed":
                logger.info("Batch processing completed!")
                break
            elif batch.status in ["failed", "canceled"]:
                logger.error(f"Batch processing {batch.status}.")
                job_metadata["error"] = f"Batch processing {batch.status}"
                with open(metadata_file_path, 'w') as f:
                    json.dump(job_metadata, f, indent=2)
                return BatchResult(metadata=job_metadata, results=[])
        
            time.sleep(10)

        output_file_path = os.path.join(output_dir, f"batch_{batch.id}_output.jsonl")
        file_response = self.openai_client.files.content(batch.output_file_id)
        with open(output_file_path, "w") as output_file:
            output_file.write(file_response.text)

        job_metadata.update({
            "status": "completed",
            "last_updated": datetime.now().isoformat(),
            "output_file_path": output_file_path
        })
        with open(metadata_file_path, 'w') as f:
            json.dump(job_metadata, f, indent=2)

        results = []
        with open(output_file_path, 'r') as f:
            for line, original_prompt in zip(f, original_prompts):
                response = json.loads(line)

                # Extract the content from the correct place in the response
                body = response['response']['body']
                choices = body['choices']

                if 'choices' in body and len(choices) > 0:
                    content = choices[0]['message']['content']

                    # Add results based on the expected response format
                    if response_format:
                        results.append({
                            "prompt": original_prompt,  # Use the original prompt here
                            "response": response_format(**json.loads(content))
                        })
                    else:
                        results.append({
                            "prompt": original_prompt,  # Use the original prompt here
                            "response": content
                        })
                else:
                    logger.error(f"Unexpected response format: {response}")
    
        return BatchResult(metadata=job_metadata, results=results)

# Example usage and test code
if __name__ == "__main__":
    handler = LLMAPIHandler()

    # Define a Pydantic model for structured responses
    class ResponseModel(BaseModel):
        answer: str
        confidence: float

    # Comment out the tests you do not wish to run

    # Test regular mode with structured output for OpenAI
    
    regular_result_openai = handler.process(
        prompts="What's the capital of France?",
        model="gpt-4o-2024-08-06",
        system_message="You are a helpful assistant.",
        temperature=0.7,
        mode="regular",
        response_format=ResponseModel
    )
    print("Regular mode result (OpenAI):", regular_result_openai)

    # Test regular mode with structured output for Claude
    """
    regular_result_claude = handler.process(
        prompts="What's the capital of Germany?",
        model="claude-3-5-sonnet-20240620",
        temperature=0.5,
        mode="regular",
        response_format=ResponseModel
    )
    print("Regular mode result (Claude):", regular_result_claude)
    """

    # Test batch mode with structured output (OpenAI only)
    
    output_dir = "batch_output"
    batch_result = handler.process(
        prompts=["What's the capital of Spain?", "What's the capital of Spain?", "What's the capital of Italy?"],
        model="gpt-4o-mini",
        mode="batch",
        response_format=ResponseModel,
        output_dir=output_dir,
        deduplicate_prompts=True  # Enable deduplication of identical prompts
    )
    print("Batch mode metadata:", batch_result.metadata)
    for result in batch_result.results:
        print("Batch result:", result)
    

    # Test async mode with structured output for OpenAI
    async_prompts = [
        "What's the capital of Canada?",
        "What's the capital of Australia?",
        "What's the capital of Brazil?",
        "What's the capital of Japan?",
        "What's the capital of India?"
    ]
    async_results = handler.process(
        prompts=async_prompts,
        model="gpt-4o-mini",
        system_message="You are a helpful assistant.",
        temperature=0.7,
        mode="async",
        response_format=ResponseModel
    )
    print("Async mode results:")
    for prompt, response in zip(async_prompts, async_results):
        if response:
            print(f"Prompt: {prompt}\nResponse: {response}\n")
        else:
            print(f"Prompt: {prompt}\nResponse: Error occurred.\n")
