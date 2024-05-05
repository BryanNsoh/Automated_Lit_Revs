import json
import asyncio
import aiohttp
from llm_api_handler import LLM_APIHandler
from prompts import get_prompt, core_search_guide


class QueryGenerator:
    def __init__(self, api_key_path, session):
        self.api_key_path = api_key_path
        self.session = session
        self.llm_api_handler = LLM_APIHandler(api_key_path, session)

    async def generate_queries(self, user_query):
        # Generate the prompt from the user's query
        prompt = get_prompt(
            template_name="generate_queries",
            user_query=user_query,
            search_guidance=core_search_guide,
        )

        # Obtain the model's response for the generated prompt
        response = await self.llm_api_handler.generate_llama_content(prompt)

        # Parse and return the response
        return self.parse_response(response)

    def parse_response(self, response):
        try:
            # Attempt to find and extract the JSON structured data
            start_index = response.find("{")
            end_index = response.rfind("}") + 1
            if start_index != -1 and end_index != -1:
                json_string = response[start_index:end_index]
                return json.loads(json_string)
            else:
                print("No valid JSON object found.")
                return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}


async def main():
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    async with aiohttp.ClientSession() as session:
        processor = QueryGenerator(api_key_path, session)
        user_query = "Impact of climate change on global water resources"
        queries = await processor.generate_queries(user_query)
        print(json.dumps(queries, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
