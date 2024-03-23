import json
import asyncio
import aiohttp
import time
import logging
import google.generativeai as genai
import anthropic
import backoff


class LLM_APIHandler:
    def __init__(self, key_path):
        """
        Initialize the LLM_APIHandler with the path to the JSON file containing API keys.
        """
        self.load_api_keys(key_path)
        self.semaphore = asyncio.Semaphore(10)  # Limit to 10 requests at a time
        self.last_request_time = 0
        self.haiku_rate_limiter = asyncio.Semaphore(
            1
        )  # Limit Haiku to 1 request per second
        self.haiku_minute_counter = 0
        self.haiku_minute_timestamp = time.time()
        genai.configure(api_key=self.gemini_api_key)
        self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)

    def load_api_keys(self, key_path):
        """
        Load the API keys from the specified JSON file.
        """
        with open(key_path, "r") as file:
            api_keys = json.load(file)
        self.gemini_api_key = api_keys["GEMINI_API_KEY"]
        self.claude_api_key = api_keys["CLAUDE_API_KEY"]

    @backoff.on_exception(backoff.expo, (aiohttp.ClientError, ValueError), max_tries=5)
    async def generate_gemini_content(self, prompt, response_format=None):
        """
        Generate content using the Gemini API.

        Args:
            prompt (str): The input prompt for content generation.
            response_format (str, optional): The desired format of the response. Defaults to None.

        Returns:
            dict or str: The generated content in JSON format if response_format is "json", otherwise the raw response text.
        """
        async with self.semaphore:
            current_time = time.time()
            elapsed_time = current_time - self.last_request_time
            if elapsed_time < 1:
                await asyncio.sleep(1 - elapsed_time)
            try:
                async with aiohttp.ClientSession() as session:
                    model = genai.GenerativeModel("gemini-pro")
                    response = await model.generate_content_async(prompt)
                    self.last_request_time = time.time()
                    if response_format == "json":
                        return self.extract_json(response.text)
                    else:
                        return response.text
            except Exception as e:
                logging.error(f"Error in Gemini API call: {e}")
                raise

    @backoff.on_exception(backoff.expo, (anthropic.APIError, ValueError), max_tries=5)
    async def generate_claude_content(
        self,
        prompt,
        system_prompt=None,
        model="claude-3-haiku-20240307",
        response_format=None,
        max_tokens=3000,
    ):
        """
        Generate content using the Claude API.

        Args:
            prompt (str): The input prompt for content generation.
            system_prompt (str, optional): The system prompt to guide the model's behavior. Defaults to None.
            model (str, optional): The Claude model to use. Defaults to "claude-3-haiku-20240307".
            response_format (str, optional): The desired format of the response. Defaults to None.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 3000.

        Returns:
            dict or str: The generated content in JSON format if response_format is specified, otherwise the raw response text.
        """
        async with self.haiku_rate_limiter:
            current_time = time.time()
            if self.haiku_minute_counter >= 20:
                elapsed_minute = current_time - self.haiku_minute_timestamp
                if elapsed_minute < 60:
                    await asyncio.sleep(60 - elapsed_minute)
                self.haiku_minute_counter = 0
                self.haiku_minute_timestamp = current_time
            self.haiku_minute_counter += 1

            if model not in ["claude-3-haiku-20240307"]:
                raise ValueError(f"Invalid model: {model}")

            messages = [{"role": "user", "content": prompt}]

            response = self.claude_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,  # Pass the system prompt directly
                messages=messages,
            )

            if response_format:
                return self.extract_json(response.content[0].text)
            else:
                return response.content[0].text

    def extract_json(self, response):
        """
        Extract JSON data from the response text.

        Args:
            response (str): The response text.

        Returns:
            dict: The extracted JSON data.

        Raises:
            ValueError: If no valid JSON is found in the response.
        """
        try:
            json_data = json.loads(response)
            if not json_data:
                raise ValueError("Empty JSON object returned")
            return json_data
        except json.JSONDecodeError:
            json_start = response.find("{")
            json_end = response.rfind("}")
            if json_start != -1 and json_end != -1:
                json_string = response[json_start : json_end + 1]
                try:
                    json_data = json.loads(json_string)
                    if not json_data:
                        raise ValueError("Empty JSON object returned")
                    return json_data
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format in the response")
            else:
                raise ValueError("No valid JSON found in the response")
