import asyncio
import aiohttp
import logging
import google.generativeai as genai
import google.api_core.exceptions
import anthropic
import backoff
import tiktoken
import time
from collections import deque
import json
import cohere
import requests
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("llm_handler.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def count_tokens(text, encoding_name="cl100k_base"):
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens


def clip_prompt(prompt, max_tokens, encoding_name="cl100k_base"):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(prompt)
    if len(tokens) > max_tokens:
        clipped_tokens = tokens[:max_tokens]
        clipped_prompt = encoding.decode(clipped_tokens)
        return clipped_prompt
    return prompt


class RateLimiter:
    def __init__(self, rps, window_size):
        self.rps = rps
        self.window_size = window_size
        self.window_start = time.monotonic()
        self.request_count = 0
        self.semaphore = asyncio.Semaphore(rps)

    async def acquire(self):
        current_time = time.monotonic()
        elapsed_time = current_time - self.window_start
        if elapsed_time > self.window_size:
            self.window_start = current_time
            self.request_count = 0
        if self.request_count >= self.rps:
            await asyncio.sleep(self.window_size - elapsed_time)
            self.window_start = time.monotonic()
            self.request_count = 0
        self.request_count += 1
        await self.semaphore.acquire()

    def release(self):
        self.semaphore.release()


class RequestTracker:
    def __init__(self):
        self.active_requests = 0
        self.total_requests = 0
        self.total_response_time = 0
        self.request_times = []
        self.throughputs = []

    def start_request(self):
        self.active_requests += 1
        self.total_requests += 1
        self.request_times.append(time.time())

    def end_request(self, response_time):
        self.active_requests -= 1
        self.total_response_time += response_time

    def calculate_metrics(self):
        elapsed_time = time.time() - self.request_times[0]
        throughput = self.total_requests / elapsed_time
        self.throughputs.append(throughput)
        avg_response_time = self.total_response_time / self.total_requests
        return {
            "active_requests": self.active_requests,
            "total_requests": self.total_requests,
            "throughput": throughput,
            "avg_response_time": avg_response_time,
        }


class LLM_APIHandler:
    def __init__(self, key_path, session, rps=0.5, window_size=60):
        self.load_api_keys(key_path)
        self.rate_limiters = [
            RateLimiter(rps, window_size) for _ in range(len(self.gemini_api_keys))
        ]
        self.claude_rate_limiter = RateLimiter(rps, window_size)
        self.cohere_rate_limiter = RateLimiter(75, 60)  # 75 calls per minute
        self.llama_rate_limiter = RateLimiter(rps, window_size)
        self.qwen_rate_limiter = RateLimiter(rps, window_size)
        self.request_tracker = RequestTracker()
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        self.gemini_clients = []
        for api_key in self.gemini_api_keys:
            genai.configure(api_key=api_key)
            client = genai.GenerativeModel(
                "gemini-pro", safety_settings=self.safety_settings
            )
            self.gemini_clients.append(client)
        self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
        self.cohere_client = cohere.Client(self.cohere_api_key)
        self.session = session
        self.client_queue = deque(range(len(self.gemini_api_keys)))  # Round-robin queue

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()  # Close the session when done

    def load_api_keys(self, key_path):
        with open(key_path, "r") as file:
            api_keys = json.load(file)
        self.gemini_api_keys = [
            api_keys[key] for key in api_keys if key.startswith("GEMINI_API_KEY")
        ]
        self.claude_api_key = api_keys["CLAUDE_API_KEY"]
        self.cohere_api_key = api_keys["COHERE_API_KEY"]
        self.together_api_key = api_keys["TOGETHER_API_KEY"]

    @backoff.on_exception(
        backoff.expo,
        (
            aiohttp.ClientError,
            ValueError,
            google.api_core.exceptions.InternalServerError,
            google.api_core.exceptions.ServiceUnavailable,
            google.api_core.exceptions.Unknown,
        ),
        max_tries=5,
        max_time=60,
        jitter=backoff.full_jitter,
    )
    async def generate_gemini_content(self, prompt):
        client_index = self.client_queue.popleft()
        self.client_queue.append(
            client_index
        )  # Move the client to the end of the queue
        rate_limiter = self.rate_limiters[client_index]
        await rate_limiter.acquire()
        try:
            retry_count = 0
            while retry_count < 5:
                try:
                    clipped_prompt = clip_prompt(prompt, max_tokens=26000)
                    logging.info(
                        f"Generating content with Gemini API (client {client_index}). Prompt: {clipped_prompt}"
                    )
                    self.request_tracker.start_request()
                    start_time = time.time()
                    response = await self.gemini_clients[
                        client_index
                    ].generate_content_async(clipped_prompt)
                    end_time = time.time()
                    response_time = end_time - start_time
                    self.request_tracker.end_request(response_time)
                    if response.text:
                        metrics = self.request_tracker.calculate_metrics()
                        logger.info(f"Gemini API Metrics: {metrics}")
                        return response.text
                    else:
                        raise ValueError("Invalid response format from Gemini API.")
                except (IndexError, AttributeError, ValueError) as e:
                    retry_count += 1
                    logger.warning(
                        f"Error from Gemini API (client {client_index}). Retry count: {retry_count}. Error: {e}"
                    )
                    await asyncio.sleep(min(2**retry_count + random.random(), 30))
                except google.api_core.exceptions.InternalServerError as e:
                    retry_count += 1
                    logger.warning(
                        f"InternalServerError from Gemini API (client {client_index}). Retry count: {retry_count}. Error: {e}"
                    )
                    await asyncio.sleep(min(2**retry_count + random.random(), 30))
                except google.api_core.exceptions.ServiceUnavailable as e:
                    retry_count += 1
                    logger.warning(
                        f"ServiceUnavailable from Gemini API (client {client_index}). Retry count: {retry_count}. Error: {e}"
                    )
                    await asyncio.sleep(min(2**retry_count + random.random(), 30))
                except google.api_core.exceptions.Unknown as e:
                    retry_count += 1
                    logger.warning(
                        f"Unknown error from Gemini API (client {client_index}). Retry count: {retry_count}. Error: {e}"
                    )
                    await asyncio.sleep(min(2**retry_count + random.random(), 30))
            logger.error(
                f"Max retries reached. Unable to generate content with Gemini API (client {client_index}). Moving on."
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error from Gemini API (client {client_index}). Error: {e}"
            )
            raise
        finally:
            rate_limiter.release()

    @backoff.on_exception(
        backoff.expo,
        (anthropic.APIError, ValueError),
        max_tries=5,
        max_time=60,
        jitter=backoff.full_jitter,
    )
    async def generate_opus_content(
        self,
        prompt,
        system_prompt=None,
        model="claude-3-opus-20240229",
        max_tokens=3000,
    ):
        await self.claude_rate_limiter.acquire()
        try:
            if model not in [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ]:
                raise ValueError(f"Invalid model: {model}")
            clipped_prompt = clip_prompt(prompt, max_tokens=180000)
            messages = [{"role": "user", "content": clipped_prompt}]
            if system_prompt is None:
                system_prompt = "Directly fulfill the user's request without preamble, paying very close attention to all nuances of their instructions."
            # logger.info(f"Generating content with Claude API. Prompt: {clipped_prompt}")
            try:
                response = self.claude_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=messages,
                )
                # logger.info(f"Claude API response: {response.content[0].text}")
                return response.content[0].text
            except anthropic.APIError as e:
                logger.error(
                    f"Max retries reached. Unable to generate content with Claude API. Error: {e}. Moving on."
                )
                return None
        finally:
            self.claude_rate_limiter.release()

    @backoff.on_exception(
        backoff.expo,
        (anthropic.APIError, ValueError),
        max_tries=5,
        max_time=60,
        jitter=backoff.full_jitter,
    )
    async def generate_haiku_content(
        self,
        prompt,
        system_prompt=None,
        model="claude-3-haiku-20240307",
        max_tokens=3000,
    ):
        await self.claude_rate_limiter.acquire()
        try:
            if model not in [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ]:
                raise ValueError(f"Invalid model: {model}")
            clipped_prompt = clip_prompt(prompt, max_tokens=180000)
            messages = [{"role": "user", "content": clipped_prompt}]
            if system_prompt is None:
                system_prompt = "Directly fulfill the user's request without preamble, paying very close attention to all nuances of their instructions."
            # logger.info(f"Generating content with Claude API. Prompt: {clipped_prompt}")
            try:
                response = self.claude_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=messages,
                )
                # logger.info(f"Claude API response: {response.content[0].text}")
                return response.content[0].text
            except anthropic.APIError as e:
                logger.error(
                    f"Max retries reached. Unable to generate content with Claude API. Error: {e}. Moving on."
                )
                return None
        finally:
            self.claude_rate_limiter.release()

    async def generate_cohere_content(
        self,
        prompt,
        model="command-r",
        temperature=0.3,
        prompt_truncation="AUTO",
        connectors=None,
    ):
        await self.cohere_rate_limiter.acquire()
        try:
            clipped_prompt = clip_prompt(prompt, max_tokens=180000)
            response = self.cohere_client.chat(
                model=model,
                message=clipped_prompt,
                temperature=temperature,
                chat_history=[],
                prompt_truncation=prompt_truncation,
                connectors=connectors,
            )
            return response.text
        except cohere.CohereError as e:
            logger.error(
                f"Unable to generate content with Cohere API. Error: {e}. Moving on."
            )
            return None
        finally:
            self.cohere_rate_limiter.release()

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ValueError),
        max_tries=5,
        max_time=60,
        jitter=backoff.full_jitter,
    )
    async def generate_llama_content(
        self,
        prompt,
        max_tokens=1024,
        temperature=0.5,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
    ):
        endpoint = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
        }
        clipped_prompt = clip_prompt(prompt, max_tokens=5000)
        messages = [{"content": clipped_prompt, "role": "user"}]
        data = {
            "model": "meta-llama/Llama-3-70b-chat-hf",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "stop": ["<|eot_id|>"],
            "messages": messages,
        }

        await self.llama_rate_limiter.acquire()  # Acquire the rate limiter
        try:
            async with self.session.post(
                endpoint, json=data, headers=headers
            ) as response:
                response.raise_for_status()
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                return content
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            logger.error(
                f"Unable to generate content with Llama API. Error: {e}. Moving on."
            )
            return None
        finally:
            self.llama_rate_limiter.release()  # Release the rate limiter

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ValueError),
        max_tries=5,
        max_time=60,
        jitter=backoff.full_jitter,
    )
    async def generate_qwen_content(
        self,
        prompt,
        max_tokens=2048,
        temperature=0.1,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
    ):
        endpoint = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
        }
        clipped_prompt = clip_prompt(prompt, max_tokens=25000)
        messages = [{"content": clipped_prompt, "role": "user"}]
        data = {
            "model": "meta-llama/Llama-3-70b-chat-hf",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "stop": ["<|im_end|>", "<|im_start|>"],
            "messages": messages,
        }

        await self.qwen_rate_limiter.acquire()  # Acquire the rate limiter
        try:
            async with self.session.post(
                endpoint, json=data, headers=headers
            ) as response:
                response.raise_for_status()
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                return content
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            logger.error(
                f"Unable to generate content with Llama API. Error: {e}. Moving on."
            )
            return None
        finally:
            self.qwen_rate_limiter.release()  # Release the rate limiter


async def main():
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    rps = 5  # Requests per second
    window_size = 60  # Window size in seconds
    async with aiohttp.ClientSession() as session:
        async with LLM_APIHandler(
            api_key_path, session, rps, window_size
        ) as api_handler:
            tasks = []

            # Llama API
            test_qwen = False
            if test_qwen:
                qwen_prompt = "What is the meaning of life?"
                tasks.append(api_handler.generate_qwen_content(prompt=qwen_prompt))

            # Gemini API
            test_gemini = False
            if test_gemini:
                gemini_prompt = "What is the meaning of life?"
                tasks.append(api_handler.generate_gemini_content(gemini_prompt))

            # Claude API
            test_claude = False
            if test_claude:
                claude_prompt = "What is the meaning of life?"
                tasks.append(api_handler.generate_opus_content(claude_prompt))

            # Cohere API
            test_cohere = True
            if test_cohere:
                cohere_prompt = "What is the meaning of life?"
                tasks.append(api_handler.generate_cohere_content(cohere_prompt))

            # Llama API
            test_llama = False
            if test_llama:
                llama_prompt = "What is the meaning of life?"
                tasks.append(api_handler.generate_llama_content(prompt=llama_prompt))

            responses = await asyncio.gather(*tasks)

            for response, api_name in zip(
                responses, ["Llama", "Cohere", "Claude", "Gemini", "qwen"]
            ):
                if response is not None:
                    print(f"{api_name} Response:", response)


if __name__ == "__main__":
    asyncio.run(main())
