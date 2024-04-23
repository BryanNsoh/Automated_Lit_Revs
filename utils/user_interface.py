import gradio as gr
import asyncio
import json
from get_search_queries import QueryGenerator
from scopus_search import ScopusSearch
from analyze_papers import PaperRanker
from synthesize_results import QueryProcessor
from web_scraper import WebScraper


async def process_query(query):
    # Step 1: Generate search queries
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    query_generator = QueryGenerator(api_key_path)
    search_queries = await query_generator.generate_queries(query)

    # Step 2: Perform Scopus search
    doi_scraper = WebScraper()
    scopus_search = ScopusSearch(doi_scraper, key_path=api_key_path)
    search_results = await scopus_search.search_and_parse_json(search_queries)
    search_results_json = json.loads(search_results)

    # Step 3: Analyze papers
    paper_ranker = PaperRanker(api_key_path)
    analyzed_papers = await paper_ranker.process_queries(search_results_json, query)

    # Step 4: Synthesize results
    query_processor = QueryProcessor(api_key_path)
    synthesized_results = await query_processor.process_query(query, analyzed_papers)

    return synthesized_results


def gradio_interface(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(process_query(query))
    return results


iface = gr.Interface(
    fn=gradio_interface,
    inputs=gr.components.Textbox(lines=2, placeholder="Enter your query..."),
    outputs="text",
    title="Research Query Processor",
    description="Enter your research query and get synthesized results.",
)

iface.launch()
