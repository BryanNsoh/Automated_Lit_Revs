import json
import asyncio
import aiohttp
import logging
import google.generativeai as genai
import anthropic
import backoff
import requests
import tiktoken
import time

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
    def __init__(self, rps=5, rpm=60):
        self.rps = rps
        self.rpm = rpm
        self.semaphore = asyncio.Semaphore(rps)
        self.request_count = 0
        self.last_minute = time.monotonic() // 60

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.release()

    async def acquire(self):
        current_minute = time.monotonic() // 60
        if current_minute != self.last_minute:
            self.last_minute = current_minute
            self.request_count = 0

        if self.request_count >= self.rpm:
            await asyncio.sleep(60 - time.monotonic() % 60)
            self.request_count = 0

        self.request_count += 1
        await self.semaphore.acquire()

    def release(self):
        self.semaphore.release()


class LLM_APIHandler:
    def __init__(self, key_path, rps=1, rpm=60):
        self.load_api_keys(key_path)
        self.rate_limiter = RateLimiter(rps, rpm)
        genai.configure(api_key=self.gemini_api_key)
        self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)

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

    def load_api_keys(self, key_path):
        with open(key_path, "r") as file:
            api_keys = json.load(file)
        self.gemini_api_key = api_keys["GEMINI_API_KEY"]
        self.claude_api_key = api_keys["CLAUDE_API_KEY"]
        self.together_api_key = api_keys["TOGETHER_API_KEY"]

    @backoff.on_exception(
        backoff.expo, (aiohttp.ClientError, ValueError), max_tries=10, max_time=60
    )
    async def generate_gemini_content(self, prompt):
        async with self.rate_limiter:
            retry_count = 0
            while retry_count < 5:
                try:
                    async with aiohttp.ClientSession() as session:
                        model = genai.GenerativeModel(
                            "gemini-pro", safety_settings=self.safety_settings
                        )
                        clipped_prompt = clip_prompt(prompt, max_tokens=25000)
                        logging.info(
                            f"Generating content with Gemini API. Prompt: {clipped_prompt}"
                        )
                        response = await model.generate_content_async(clipped_prompt)
                        if response.text:
                            return response.text
                        else:
                            raise ValueError("Invalid response format from Gemini API.")
                except (IndexError, AttributeError, ValueError) as e:
                    retry_count += 1
                    logger.warning(
                        f"Error from Gemini API. Retry count: {retry_count}. Error: {e}"
                    )
                    logger.warning(f"Here is the response: {response.prompt_feedback}")
                    await asyncio.sleep(
                        min(2**retry_count, 30)
                    )  # Exponential backoff capped at 60 seconds
            logger.error(
                "Max retries reached. Unable to generate content with Gemini API. Moving on."
            )
            return None

    @backoff.on_exception(
        backoff.expo, (anthropic.APIError, ValueError), max_tries=5, max_time=60
    )
    async def generate_claude_content(
        self,
        prompt,
        system_prompt=None,
        model="claude-3-haiku-20240307",
        max_tokens=3000,
    ):
        async with self.rate_limiter:
            if model not in ["claude-3-haiku-20240307"]:
                raise ValueError(f"Invalid model: {model}")
            clipped_prompt = clip_prompt(prompt, max_tokens=180000)
            messages = [{"role": "user", "content": clipped_prompt}]
            if system_prompt is None:
                system_prompt = "Directly fulfill the user's request without preamble, paying very close attention to all nuances of their instructions."
            logger.info(f"Generating content with Claude API. Prompt: {clipped_prompt}")
            try:
                response = self.claude_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=messages,
                )
                logger.info(f"Claude API response: {response.content[0].text}")
                return response.content[0].text
            except anthropic.APIError as e:
                logger.error(
                    f"Max retries reached. Unable to generate content with Claude API. Error: {e}. Moving on."
                )
                return None

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ValueError),
        max_tries=5,
        max_time=60,
    )
    async def generate_together_content(
        self,
        prompt,
        model="Qwen/Qwen1.5-72B-Chat",
        max_tokens="null",
        temperature=0.25,
        top_p=0.5,
        top_k=20,
        repetition_penalty=1.23,
        stop=None,
        messages=None,
    ):
        async with self.rate_limiter:
            endpoint = "https://api.together.xyz/v1/chat/completions"
            if stop is None:
                stop = ["<|im_end|>", "<|im_start|>"]
            clipped_prompt = clip_prompt(prompt, max_tokens=25000)
            if messages is None:
                messages = [{"content": clipped_prompt, "role": "user"}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repetition_penalty": repetition_penalty,
                "stop": stop,
                "messages": messages,
                "repetitive_penalty": repetition_penalty,
            }
            headers = {"Authorization": f"Bearer {self.together_api_key}"}
            retry_count = 0
            while retry_count < 5:
                try:
                    response = requests.post(endpoint, json=data, headers=headers)
                    response.raise_for_status()
                    logger.info(f"Together API response: {response.text}")
                    response_data = response.json()
                    generated_text = response_data["choices"][0]["message"]["content"]
                    return generated_text
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    logger.warning(
                        f"Error from Together API. Retry count: {retry_count}. Error: {e}"
                    )
                    await asyncio.sleep(
                        min(2**retry_count, 60)
                    )  # Exponential backoff capped at 60 seconds
            logger.error(
                "Max retries reached. Unable to generate content with Together API. Moving on."
            )
            return None


async def main():
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    rps = 5  # Requests per second
    rpm = 60  # Requests per minute
    api_handler = LLM_APIHandler(api_key_path, rps, rpm)

    # Test Gemini API
    gemini_prompt = "What is the meaning of life?"
    gemini_response = await api_handler.generate_gemini_content(gemini_prompt)
    print("Gemini Response:")
    print(gemini_response)
    print()

    # Test Claude API
    claude_prompt = "What is the meaning of life?"
    claude_response = await api_handler.generate_claude_content(claude_prompt)
    print("Claude Response:")
    print(claude_response)
    print()

    # Test Together API
    together_prompt = "What is the meaning of life?"
    together_response = await api_handler.generate_together_content(together_prompt)
    print("Together Response:")
    print(together_response)
    print()


if __name__ == "__main__":
    asyncio.run(main())
