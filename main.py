from utils.research_paper_outline_generator import ResearchPaperOutlineGenerator
from utils.llm_api_handler import LLM_APIHandler
from utils.get_search_queries import QueryGenerator
from utils.google_scholar_search import GoogleScholarScraper

import asyncio

# Example usage
yaml_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\research_paper_outline.yaml"
output_directory = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3"
api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"


# section_title = "DATA COLLECTION TO CLOUD: AUTOMATION AND REAL-TIME PROCESSING"
# section_number = 3

# processor = QueryGenerator(api_key_path)
# asyncio.run(processor.process_yaml(yaml_path, section_title, section_number))

filled_yaml_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline_queries.yaml"
scraper = GoogleScholarScraper(filled_yaml_file)


# create async function to run the scraper
async def main():
    await scraper.process_queries()


# run the scraper
asyncio.run(main())


# asyncio.run(gemini_example(prompt))
# asyncio.run(haiku_example())
