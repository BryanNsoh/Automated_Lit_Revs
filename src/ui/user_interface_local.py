# utils/user_interface.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gradio as gr
import json
import aiohttp
import logging
from src.core.query_generator import QueryGenerator
from src.api.scopus_search import ScopusSearch
from src.core.paper_analyzer import PaperRanker
from src.core.result_synthesizer import QueryProcessor
from src.utils.web_scraper import WebScraper
from src.api.core_search import CORESearch
from src.utils.misc_utils import get_api_keys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("research_query_processor.log"),
        logging.StreamHandler(),
    ],
)


class ResearchQueryProcessor:
    def __init__(self):
        self.api_keys = get_api_keys()
        self.session = None

    async def chatbot_response(self, message, history):
        async with aiohttp.ClientSession() as session:
            self.session = session
            logging.info(f"Received message: {message}")

            yield "Generating search queries..."
            query_generator = QueryGenerator(self.session)
            search_queries = await query_generator.generate_queries(message)
            logging.info(f"Generated search queries: {search_queries}")

            yield "Searching in Scopus..."
            doi_scraper = WebScraper(self.session)
            scopus_search = ScopusSearch(doi_scraper, self.session)
            search_results = await scopus_search.search_and_parse_json(search_queries)
            search_results = json.loads(search_results)
            logging.info(f"Scopus search results: {search_results}")

            yield "Analyzing papers..."
            paper_ranker = PaperRanker(self.session)
            analyzed_papers = await paper_ranker.process_queries(
                search_results, message
            )
            logging.info(f"Analyzed papers: {analyzed_papers}")

            yield "Synthesizing results..."
            query_processor = QueryProcessor(self.session)
            synthesized_results = await query_processor.process_query(
                message, analyzed_papers
            )
            logging.info(f"Synthesized results: {synthesized_results}")

            yield f"{synthesized_results}"


def create_app():
    processor = ResearchQueryProcessor()

    chat_interface = gr.ChatInterface(
        fn=processor.chatbot_response,
        title="Literature Review Agent",
        description="Enter your research query below.",
        theme=gr.themes.Soft(),
    )

    return chat_interface


# Run the app
if __name__ == "__main__":
    app = create_app()
    app.launch()
