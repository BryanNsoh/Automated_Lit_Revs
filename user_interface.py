# user_interface.py

import sys
import os
import gradio as gr
import json
import aiohttp
import logging
from get_search_queries import QueryGenerator
from scopus_search import ScopusSearch
from analyze_papers import PaperRanker
from synthesize_results import QueryProcessor
from web_scraper import WebScraper
from core_search import CORESearch
from misc_utils import get_api_keys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(
            sys.stdout
        ),  # Adjusted to log to stdout for cloud environments
    ],
)


class ResearchQueryProcessor:
    def __init__(self):
        self.api_keys = get_api_keys()
        self.session = None

    async def chatbot_response(self, message):
        async with aiohttp.ClientSession() as session:
            self.session = session
            logging.info(f"Received message: {message}")

            responses = ["Generating search queries..."]
            query_generator = QueryGenerator(self.session)
            search_queries = await query_generator.generate_queries(message)
            logging.info(f"Generated search queries: {search_queries}")

            responses.append("Searching research database...")
            core_search = CORESearch(max_results=5)
            search_results = await core_search.search_and_parse_json(search_queries)
            logging.info(json.dumps(search_results, indent=4, sort_keys=True))

            responses.append("Analyzing papers...")
            paper_ranker = PaperRanker(self.session)
            analyzed_papers = await paper_ranker.process_queries(
                search_results, message
            )
            logging.info(f"Analyzed papers: {analyzed_papers}")

            responses.append("Synthesizing results...")
            query_processor = QueryProcessor(self.session)
            synthesized_results = await query_processor.process_query(
                message, analyzed_papers
            )
            logging.info(f"Synthesized results: {synthesized_results}")

            responses.append(f"{synthesized_results}")
            return responses


def create_app():
    processor = ResearchQueryProcessor()

    chat_interface = gr.ChatInterface(
        fn=processor.chatbot_response,
        title="Literature Review Agent",
        description="Enter your research query below.",
        theme=gr.themes.Soft(),
    )

    return chat_interface.app


# Run the app
if __name__ == "__main__":
    app = create_app()
    app.launch()
