import gradio as gr
import json
import aiohttp
import logging
from get_search_queries import QueryGenerator
from scopus_search import ScopusSearch
from analyze_papers import PaperRanker
from synthesize_results import QueryProcessor
from web_scraper import WebScraper

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
    def __init__(self, api_key_path):
        self.api_key_path = api_key_path
        self.session = None

    async def chatbot_response(self, message, history):
        async with aiohttp.ClientSession() as session:
            self.session = session
            logging.info(f"Received message: {message}")

            yield "Generating search queries..."
            query_generator = QueryGenerator(self.api_key_path, self.session)
            search_queries = await query_generator.generate_queries(message)
            logging.info(f"Generated search queries: {search_queries}")

            yield "Searching in Scopus..."
            doi_scraper = WebScraper(self.session)
            scopus_search = ScopusSearch(doi_scraper, self.api_key_path, self.session)
            search_results = await scopus_search.search_and_parse_json(search_queries)
            search_results_json = json.loads(search_results)
            logging.info(f"Scopus search results: {search_results_json}")

            yield "Analyzing papers..."
            paper_ranker = PaperRanker(self.api_key_path, self.session)
            analyzed_papers = await paper_ranker.process_queries(
                search_results_json, message
            )
            logging.info(f"Analyzed papers: {analyzed_papers}")

            yield "Synthesizing results..."
            query_processor = QueryProcessor(self.api_key_path, self.session)
            synthesized_results = await query_processor.process_query(
                message, analyzed_papers
            )
            logging.info(f"Synthesized results: {synthesized_results}")

            yield f"Completed! Here are your results: {synthesized_results}"


def main():
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    processor = ResearchQueryProcessor(api_key_path)
    chat_interface = gr.ChatInterface(
        fn=processor.chatbot_response,
        title="Literature Review Agent",
        description="Enter your research query below.",
        theme=gr.themes.Soft(),
    )
    chat_interface.launch(share=True)


if __name__ == "__main__":
    main()