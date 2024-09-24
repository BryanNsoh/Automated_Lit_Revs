import os
import json
import time
import logging
import asyncio
from typing import List, Dict, Any, Union, Type, Generic, TypeVar

from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv

# Import synchronous and asynchronous OpenAI clients
from openai import AsyncOpenAI, OpenAI  # Corrected import statement
import anthropic

# Import AsyncLimiter for rate limiting
from aiolimiter import AsyncLimiter

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(override=True)

# Retrieve API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

T = TypeVar('T', bound=BaseModel)

class BatchResult(BaseModel, Generic[T]):
    metadata: Dict[str, Any]
    results: List[Dict[str, Union[str, T]]]

class LLMAPIHandler:
    """
    Handles interactions with OpenAI and Anthropic models for processing prompts in both regular and batch modes.
    Supports deduplication of prompts, structured outputs via Pydantic models, 
    and batch processing with custom configurations like temperature and system messages.
    """

    def __init__(self):
        # Initialize synchronous clients
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # Initialize asynchronous clients
        self.async_openai_client = AsyncOpenAI(api_key=openai_api_key)
        # Assuming Anthropic also provides an asynchronous client
        self.async_anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
        
        # Initialize rate limiter: 2000 requests per minute
        self.limiter = AsyncLimiter(max_rate=2000, time_period=60)
        
    def process(self, 
                prompts: Union[str, List[str]],
                model: str = "gpt-4o-mini",
                system_message: str = None,
                temperature: float = 0.7,
                mode: str = "regular",
                response_format: Union[None, Type[T]] = None,
                output_dir: str = None,
                update_interval: int = 60,
                deduplicate_prompts: bool = False) -> Union[Any, T, BatchResult[T]]:
        """
        Process a prompt or list of prompts using the specified model.
        """
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
            raise ValueError("Invalid input: 'prompts' should be a string for regular mode or a list for batch mode.")

    async def async_process(self,
                            prompts: List[str],
                            model: str = "gpt-4o-mini",
                            system_message: str = None,
                            temperature: float = 0.7,
                            response_format: Union[None, Type[T]] = None) -> List[Union[str, T]]:
        """
        Asynchronously process a list of prompts in regular mode and return Pydantic model instances.
        
        Args:
            prompts: List of prompt strings to process.
            model: Model name to use for processing.
            system_message: Optional system message to guide model behavior.
            temperature: Sampling temperature for responses.
            response_format: Pydantic model to structure the response.
        
        Returns:
            List of responses (either strings or Pydantic model instances) corresponding to each prompt.
        """
        tasks = [
            self._async_process_regular({
                "model": model,
                "prompt": prompt,
                "system_message": system_message,
                "temperature": temperature
            }, response_format)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)

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
            schema = response_format.model_json_schema()
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

    async def _async_process_regular(self, request: Dict[str, Any], response_format: Union[None, Type[T]]) -> Union[str, T]:
        """Asynchronously process a regular request with a single prompt."""
        model = request['model']
        temperature = request.get('temperature', 0.7)
        prompt = request['prompt']
        system_message = self._get_system_message(request.get('system_message'), response_format)

        async with self.limiter:
            if model in ['gpt-4o-mini', 'gpt-4o-2024-08-06']:
                messages = [{"role": "user", "content": prompt}]
                if system_message:
                    messages.insert(0, {"role": "system", "content": system_message})

                if response_format:
                    completion = await self.async_openai_client.beta.chat.completions.parse(
                        model=model,
                        messages=messages,
                        response_format=response_format
                    )
                    return completion.choices[0].message.parsed
                else:
                    response = (await self.async_openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature
                    )).choices[0].message.content
                    return response

            elif model == 'claude-3-5-sonnet-20240620':
                if response_format:
                    schema = response_format.model_json_schema()
                    prompt = f"Answer exclusively in this JSON format: {schema}\n\n{prompt}"

                message = await self.async_anthropic_client.messages.create(
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

    def _process_batch(self, requests: List[Dict[str, Any]], response_format: Union[None, Type[T]], output_dir: str, update_interval: int, original_prompts: List[str]) -> BatchResult[T]:
        """Process a batch of requests and return a list of dictionaries matching prompt and response."""
        os.makedirs(output_dir, exist_ok=True)

        batch_file_path = os.path.join(output_dir, 'batch_input.jsonl')
        with open(batch_file_path, 'w') as f:
            for request in requests:
                messages = [{"role": "user", "content": request['prompt']}]
                if 'system_message' in request and request['system_message']:
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
                body = response['response']['body']
                choices = body['choices']

                if 'choices' in body and len(choices) > 0:
                    content = choices[0]['message']['content']

                    if response_format:
                        results.append({
                            "prompt": original_prompt,
                            "response": response_format(**json.loads(content))
                        })
                    else:
                        results.append({
                            "prompt": original_prompt,
                            "response": content
                        })
                else:
                    logger.error(f"Unexpected response format: {response}")

        return BatchResult(metadata=job_metadata, results=results)

# Example usage and test code
if __name__ == "__main__":
    handler = LLMAPIHandler()

    # Test regular mode with structured output for OpenAI
    class ResponseModel(BaseModel):
        answer: str
        confidence: float

    regular_result_openai = handler.process(
        prompts="What's the capital of France?",
        model="gpt-4o-mini",
        system_message="You are a helpful assistant.",
        temperature=0.7,
        mode="regular",
        response_format=ResponseModel
    )
    print("Regular mode result (OpenAI):", regular_result_openai)
    """
    # Test regular mode with structured output for Claude
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

    # Test asynchronous processing
    async def test_async_processing():
        async_batch_result = await handler.async_process(
            prompts=["What's the capital of Portugal?", "What's the capital of Netherlands?", "What's the capital of Belgium?"],
            model="gpt-4o-mini",
            system_message="You are a helpful assistant.",
            temperature=0.6,
            response_format=ResponseModel
        )
        print("Asynchronous processing results:")
        for res in async_batch_result:
            print(res)

    asyncio.run(test_async_processing())
