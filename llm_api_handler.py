import os
import json
import time
import logging
from openai import OpenAI
import anthropic
from typing import List, Dict, Any, Union, Type, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

openai_client = OpenAI(api_key=openai_api_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class BatchResult(BaseModel, Generic[T]):
    metadata: Dict[str, Any]
    results: List[Dict[str, Union[str, T]]]


class LLMAPIHandler:
    """
    Handles interactions with OpenAI and Anthropic models for processing prompts in both regular and batch modes.
    
    This handler supports deduplication of prompts, structured outputs via Pydantic models, 
    and batch processing with custom configurations like temperature and system messages.
    
    Methods:
    --------
    process(prompts, model, system_message, temperature, mode, response_format, output_dir, update_interval, deduplicate_prompts):
        Processes one or more prompts using the specified model.
    
    _construct_batch_requests(prompts, model, temperature):
        Constructs batch requests with unique custom IDs.
    
    _get_system_message(user_system_message, response_format):
        Generates the appropriate system message based on the response format or user input.
    
    _process_regular(request, response_format):
        Handles processing of a single prompt in regular mode.
    
    _process_batch(requests, response_format, output_dir, update_interval, original_prompts):
        Handles processing of multiple prompts in batch mode, managing file output and job status.
    
    Parameters:
    -----------
    prompts: Union[str, List[str]]
        A single prompt (string) or a list of prompts to be processed.
    
    model: str
        The model to be used for processing the prompts. Examples include 'gpt-4o-mini', 'gpt-4o-2024-08-06', or 'claude-3-5-sonnet-20240620'.
    
    system_message: Optional[str]
        An optional system message that guides the behavior of the model (OpenAI models only). 
        This message can be used to provide specific instructions to the model on how to respond.
    
    temperature: float
        A sampling temperature for controlling randomness. The default value is 0.7. 
        Lower values make the model's responses more deterministic.
    
    mode: str
        Either 'regular' or 'batch'. Determines if the handler processes a single prompt or a batch of prompts. 
        In 'regular' mode, the handler processes a single prompt. In 'batch' mode, it handles multiple prompts at once.
    
    response_format: Optional[Type[T]]
        If provided, the response will be parsed into this Pydantic model. This allows for structured outputs like JSON responses.
        If None, the raw text from the model will be returned.
    
    output_dir: Optional[str]
        The directory where batch mode results will be saved. This is required for batch mode and ignored in regular mode.
    
    update_interval: int
        The interval (in seconds) for checking the status of a batch job. The default is 60 seconds.
    
    deduplicate_prompts: bool
        If True, removes duplicate prompts in batch mode before processing them. The default is False, meaning no deduplication.
    
    Returns:
    --------
    For 'regular' mode:
        - If response_format is provided: A Pydantic model instance containing the structured response.
        - If response_format is not provided: A string containing the raw response from the model.
    
    For 'batch' mode:
        - A BatchResult object containing metadata about the batch job and a list of dictionaries with:
            - 'prompt': The original prompt.
            - 'response': The model's response (structured or raw based on response_format).
    
    Raises:
    -------
    ValueError:
        If the 'prompts' parameter is not a string or a list of strings.
    
    Examples:
    ---------
    Regular Mode (OpenAI with Pydantic response):
    >>> handler = LLMAPIHandler()
    >>> class ResponseModel(BaseModel):
    >>>     answer: str
    >>>     confidence: float
    >>> result = handler.process(
    >>>     prompts="What is the capital of France?",
    >>>     model="gpt-4o-2024-08-06",
    >>>     response_format=ResponseModel,
    >>>     mode="regular"
    >>> )
    >>> print(result.answer)  # Output: "Paris"
    
    Batch Mode (With Deduplication):
    >>> batch_result = handler.process(
    >>>     prompts=["What's the capital of Spain?", "What's the capital of Spain?", "What's the capital of Italy?"],
    >>>     model="gpt-4o-mini",
    >>>     mode="batch",
    >>>     response_format=ResponseModel,
    >>>     output_dir="batch_output",
    >>>     deduplicate_prompts=True
    >>> )
    >>> for result in batch_result.results:
    >>>     print(f"Prompt: {result['prompt']}, Answer: {result['response'].answer}")
    
    Notes:
    ------
    - When using batch mode, make sure to provide an 'output_dir' where batch results will be stored.
    - The 'deduplicate_prompts' flag, if set to True, ensures that repeated prompts are sent only once to the model.
    - The response_format must be a Pydantic model to enable structured output. If omitted, the raw model response (text) is returned.
    """

    def __init__(self):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

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

        Args:
            prompts: Either a single prompt (str) or a list of prompts (for batch mode).
            model: Model name (e.g., 'gpt-4o-mini').
            system_message: Optional system message for setting behavior (OpenAI only).
            temperature: Sampling temperature (default is 0.7).
            mode: 'regular' or 'batch'.
            response_format: Optional Pydantic model for structured output.
            output_dir: Directory for batch mode output (required for batch mode).
            update_interval: Interval for batch status updates.
            deduplicate_prompts: If True, deduplicate prompts before sending (default: False).

        Returns:
            For 'regular' mode: 
                - The model's response (either a string or a Pydantic model instance if response_format is provided).
            For 'batch' mode:
                - A BatchResult object containing:
                    - metadata about the batch job.
                    - A list of dictionaries, each with:
                        - 'prompt': The original prompt.
                        - 'response': The corresponding model's response (either string or Pydantic model).
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

    def _construct_batch_requests(self, prompts: List[str], model: str, temperature: float) -> List[Dict[str, Any]]:
        """
        Construct a list of batch requests with the prompts, including unique custom IDs.

        Args:
            prompts: A list of prompt strings.
            model: Model name to be used in each request.
            temperature: Sampling temperature for each request.

        Returns:
            A list of dictionaries representing batch requests.
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
                schema = response_format.schema_json()
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

    def _process_batch(self, requests: List[Dict[str, Any]], response_format: Union[None, Type[T]], output_dir: str, update_interval: int, original_prompts: List[str]) -> BatchResult[T]:
        """Process a batch of requests and return a list of dictionaries matching prompt and response."""
        os.makedirs(output_dir, exist_ok=True)

        batch_file_path = os.path.join(output_dir, 'batch_input.jsonl')
        with open(batch_file_path, 'w') as f:
            for request in requests:
                messages = [{"role": "user", "content": request['prompt']}]
                if 'system_message' in request:
                    messages.insert(0, {"role": "system", "content": request['system_message']})
                
                if response_format:
                    schema = response_format.schema_json()
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

    # Test regular mode with structured output for OpenAI
    class ResponseModel(BaseModel):
        answer: str
        confidence: float

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
    regular_result_claude = handler.process(
        prompts="What's the capital of Germany?",
        model="claude-3-5-sonnet-20240620",
        temperature=0.5,
        mode="regular",
        response_format=ResponseModel
    )
    print("Regular mode result (Claude):", regular_result_claude)

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
