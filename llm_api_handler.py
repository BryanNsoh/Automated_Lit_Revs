import asyncio
import aiohttp
import tiktoken
import time
import requests
from misc_utils import get_api_keys
from openai import AsyncOpenAI
import os
import backoff
from logger_config import get_logger

logger = get_logger(__name__)


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


class LLM_APIHandler:
    def __init__(self, api_keys, session, rps=5, window_size=60):
        self.set_api_keys(api_keys)
        self.openai_rate_limiter = RateLimiter(rps, window_size)
        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()  # Close the session when done

    def set_api_keys(self, api_keys):
        self.openai_api_key = api_keys["OPENAI_API_KEY"]
        self.together_api_key = api_keys["TOGETHER_API_KEY"]

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=5,
        max_time=60,
        jitter=backoff.full_jitter,
    )
    async def generate_openai_content(self, prompt, model="gpt-4o-mini"):
        await self.openai_rate_limiter.acquire()
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            messages = [{"role": "user", "content": prompt}]
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                top_p=1,
                n=1,
                stream=False,
                max_tokens=None,
                presence_penalty=0,
                frequency_penalty=0,
                user=None,
            )
            if response:
                return response.choices[0].message.content
            else:
                return "No response from API."
        except Exception as e:
            logger.error(
                f"Unable to generate content with OpenAI API. Error: {e}. Moving on."
            )
            return None
        finally:
            self.openai_rate_limiter.release()


async def main():
    api_keys = get_api_keys(source="local" if os.getenv("ENVIRONMENT") == "local" else "env")
    rps = 5  # Requests per second
    window_size = 60  # Window size in seconds
    async with aiohttp.ClientSession() as session:
        async with LLM_APIHandler(api_keys, session, rps, window_size) as api_handler:
            tasks = []

            # OpenAI API
            test_openai = True
            if test_openai:
                openai_prompt = "What is the meaning of life?"
                tasks.append(api_handler.generate_openai_content(openai_prompt))

            responses = await asyncio.gather(*tasks)

            for response, api_name in zip(
                responses, ["OpenAI"]
            ):
                if response is not None:
                    print(f"{api_name} Response:", response)


if __name__ == "__main__":
    asyncio.run(main())
