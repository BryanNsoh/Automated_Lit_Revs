import json
import asyncio
import aiohttp
import logging
import google.generativeai as genai
import anthropic
import backoff
import requests

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


class LLM_APIHandler:
    def __init__(self, key_path):
        self.load_api_keys(key_path)
        self.gemini_semaphore = asyncio.Semaphore(
            1
        )  # Limit Gemini to 1 request per second
        self.claude_semaphore = asyncio.Semaphore(
            1
        )  # Limit Claude to 1 request per second
        self.together_semaphore = asyncio.Semaphore(
            1
        )  # Limit Together to 1 request per second
        genai.configure(api_key=self.gemini_api_key)
        self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)

    def load_api_keys(self, key_path):
        with open(key_path, "r") as file:
            api_keys = json.load(file)
        self.gemini_api_key = api_keys["GEMINI_API_KEY"]
        self.claude_api_key = api_keys["CLAUDE_API_KEY"]
        self.together_api_key = api_keys["TOGETHER_API_KEY"]

    @backoff.on_exception(backoff.expo, (aiohttp.ClientError, ValueError), max_tries=5)
    async def generate_gemini_content(self, prompt):
        async with self.gemini_semaphore:
            await asyncio.sleep(1)  # Wait for 1 second before making the request
            retry_count = 0
            while retry_count < 5:
                try:
                    async with aiohttp.ClientSession() as session:
                        model = genai.GenerativeModel("gemini-pro")
                        logging.info(
                            f"Generating content with Gemini API. Prompt: {prompt}"
                        )
                        response = await model.generate_content_async(prompt)
                        if response.text:
                            return response.text
                        else:
                            raise ValueError("Invalid response format from Gemini API.")
                except (IndexError, AttributeError, ValueError) as e:
                    retry_count += 1
                    logger.warning(
                        f"Error from Gemini API. Retry count: {retry_count}. Error: {e}"
                    )
                    await asyncio.sleep(2**retry_count)  # Exponential backoff
            logger.error(
                "Max retries reached. Unable to generate content with Gemini API."
            )
            raise Exception(
                "Max retries reached. Unable to generate content with Gemini API."
            )

    @backoff.on_exception(backoff.expo, (anthropic.APIError, ValueError), max_tries=5)
    async def generate_claude_content(
        self,
        prompt,
        system_prompt=None,
        model="claude-3-haiku-20240307",
        max_tokens=3000,
    ):
        async with self.claude_semaphore:
            await asyncio.sleep(1)  # Wait for 1 second before making the request
            if model not in ["claude-3-haiku-20240307"]:
                raise ValueError(f"Invalid model: {model}")
            messages = [{"role": "user", "content": prompt}]
            if system_prompt is None:
                system_prompt = "Directly fulfill the user's request without preamble, paying very close attention to all nuances of their instructions."
            logger.info(f"Generating content with Claude API. Prompt: {prompt}")
            response = self.claude_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
            )
            logger.info(f"Claude API response: {response.content[0].text}")
            return response.content[0].text

    @backoff.on_exception(
        backoff.expo, (requests.exceptions.RequestException, ValueError), max_tries=5
    )
    async def generate_together_content(
        self,
        prompt,
        model="Qwen/Qwen1.5-72B-Chat",
        max_tokens=1829,
        temperature=0.25,
        top_p=0.5,
        top_k=20,
        repetition_penalty=1.23,
        stop=None,
        messages=None,
    ):
        async with self.together_semaphore:
            await asyncio.sleep(1)  # Wait for 1 second before making the request
            endpoint = "https://api.together.xyz/v1/chat/completions"
            if stop is None:
                stop = ["<|im_end|>", "<|im_start|>"]
            if messages is None:
                messages = [{"content": prompt, "role": "user"}]
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
                    await asyncio.sleep(2**retry_count)  # Exponential backoff
            logger.error(
                "Max retries reached. Unable to generate content with Together API."
            )
            raise Exception(
                "Max retries reached. Unable to generate content with Together API."
            )


async def main():
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    api_handler = LLM_APIHandler(api_key_path)

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
