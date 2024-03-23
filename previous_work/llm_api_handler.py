import json
import asyncio
import aiohttp
import time
import logging
import google.generativeai as genai


class LLM_APIHandler:
    def __init__(self, key_path):
        self.load_api_keys(key_path)
        self.semaphore = asyncio.Semaphore(10)  # Limit to 5 requests at a time
        self.last_request_time = 0
        genai.configure(api_key=self.gemini_api_key)

    def load_api_keys(self, key_path):
        with open(key_path, "r") as file:
            api_keys = json.load(file)
            self.gemini_api_key = api_keys["GEMINI_API_KEY"]

    async def generate_gemini_content(self, prompt):
        async with self.semaphore:
            current_time = time.time()
            elapsed_time = current_time - self.last_request_time
            if elapsed_time < 1:
                await asyncio.sleep(1 - elapsed_time)
            try:
                async with aiohttp.ClientSession() as session:
                    model = genai.GenerativeModel("gemini-pro")
                    response = await model.generate_content_async(prompt)
                    # print(response.text)
                    self.last_request_time = time.time()
                    return self.extract_json(response.text)
            except Exception as e:
                logging.error(f"Error in Gemini API call: {e}")
                raise

    def extract_json(self, response):
        try:
            # Try to parse the response as JSON directly
            json_data = json.loads(response)
            if not json_data:
                raise ValueError("Empty JSON object returned")
            return json_data
        except json.JSONDecodeError:
            # If parsing fails, try to find valid JSON within the response
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
