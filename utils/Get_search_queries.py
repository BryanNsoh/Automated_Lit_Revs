import json
import asyncio
import aiohttp
from llm_api_handler import LLM_APIHandler
from prompts import get_prompt, scopus_search_guide


class QueryGenerator:
    def __init__(self, api_key_path, session, max_retries=10):
        self.llm_api_handler = LLM_APIHandler(api_key_path, session)
        self.session = session
        self.max_retries = max_retries

    async def generate_queries(self, query):
        retry_count = 0
        while retry_count < self.max_retries:
            prompt = get_prompt(
                template_name="generate_queries",
                point_content=query,
                search_guidance=scopus_search_guide,
            )
            response = await self.llm_api_handler.generate_cohere_content(prompt)
            queries = self.parse_response(response)
            if queries:
                return queries
            retry_count += 1
            print(f"Retrying... Attempt {retry_count}")
        print("Max retries reached. Returning empty queries.")
        return {}

    def parse_response(self, response):
        try:
            start_index = response.find("{")
            end_index = response.rfind("}")
            if start_index != -1 and end_index != -1:
                json_string = response[start_index : end_index + 1]
                queries = json.loads(json_string)
                print(f"Queries generated: {len(queries)}")
                return queries
            else:
                print("No valid JSON object found. Returning empty queries.")
                return {}
        except json.JSONDecodeError:
            print("Error parsing JSON. Returning empty queries.")
            return {}


async def main(query):
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    async with aiohttp.ClientSession() as session:
        processor = QueryGenerator(api_key_path, session)
        queries = await processor.generate_queries(query)
        print(json.dumps(queries, indent=2))


if __name__ == "__main__":
    query = "heart disease in chickens"
    asyncio.run(main(query))
