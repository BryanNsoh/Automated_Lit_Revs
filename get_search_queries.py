import json
import asyncio
import aiohttp

from llm_api_handler import LLM_APIHandler
from prompt_loader import get_prompt
from misc_utils import get_api_keys

from logger_config import get_logger

logger = get_logger(__name__)


class QueryGenerator:
    def __init__(self, session):
        self.api_keys = get_api_keys()
        self.session = session
        self.llm_api_handler = LLM_APIHandler(self.api_keys, session)

    async def generate_queries(self, user_query):
        dependencies = {"search_guidance": "core_search_guide"}
        # Generate the prompt from the user's query
        prompt = get_prompt(
            template_name="generate_queries",
            dependencies=dependencies,
            user_query=user_query,
        )

        # Obtain the model's response for the generated prompt
        response = await self.llm_api_handler.generate_openai_content(prompt)

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
    async with aiohttp.ClientSession() as session:
        processor = QueryGenerator(session)
        user_query = "Impact of climate change on global water resources"
        queries = await processor.generate_queries(user_query)
        print(json.dumps(queries, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
