from utils.research_paper_outline_generator import ResearchPaperOutlineGenerator
from utils.llm_api_handler import LLM_APIHandler
from utils.populate_search_queries import QueryGenerator
from utils.google_scholar_search import GoogleScholarScraper
from utils.scopus_search import ScopusSearch

import asyncio

# Example usage
yaml_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\research_paper_outline.yaml"
output_directory = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3"
api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"


# test the QueryGenerator
