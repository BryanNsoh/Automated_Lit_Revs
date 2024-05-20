import asyncio
import logging
from llm_api_handler import LLM_APIHandler
from prompts import get_prompt
import aiohttp
from misc_utils import get_api_keys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryProcessor:
    def __init__(self, session):
        api_keys = get_api_keys()
        self.llm_api_handler = LLM_APIHandler(api_keys, session)

    async def process_query(self, user_query, returned_results):
        prompt = get_prompt(
            template_name="synthesize_results",
            user_query=user_query,
            returned_results=returned_results,
        )

        try:
            logger.info(f"Processing query: {user_query}")
            response = await self.llm_api_handler.generate_openai_content(prompt)
            return response
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return None


async def main():
    async with aiohttp.ClientSession() as session:
        query_processor = QueryProcessor(session)
        user_query = "What are the latest advancements in artificial intelligence?"
        returned_results = [
            "AI has made significant progress in fields such as computer vision and natural language processing.",
            "Deep learning techniques have revolutionized AI, enabling machines to learn from large datasets.",
            "AI is being applied in various domains, including healthcare, finance, and autonomous vehicles.",
        ]

        logger.info("Starting query processing...")
        response = await query_processor.process_query(user_query, returned_results)
        if response:
            logger.info(f"Response: {response}")
        else:
            logger.warning("Failed to generate a response.")
        logger.info("Query processing completed.")


if __name__ == "__main__":
    asyncio.run(main())
