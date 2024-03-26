import asyncio
import logging
from pathlib import Path

from openalex_search import OpenAlexPaperSearch
from scopus_search import ScopusSearch
from yaml_iterator import IrrigationData
from web_scraper import WebScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryProcessor:
    def __init__(self, yaml_file, output_folder, api_key_path, email):
        self.yaml_file = yaml_file
        self.output_folder = Path(output_folder)
        self.api_key_path = api_key_path
        self.email = email
        self.web_scraper = WebScraper()
        self.openalex_search = OpenAlexPaperSearch(
            email, self.web_scraper, self.output_folder
        )
        self.scopus_search = ScopusSearch(
            api_key_path, self.web_scraper, self.output_folder
        )
        self.irrigation_data = IrrigationData(yaml_file)

    async def process_queries(self):
        try:
            await self.irrigation_data.load_data()  # Load the YAML data before iteration
            query_tasks = []
            async for (
                subsection,
                point_title,
                query_type,
                query_id,
                response_id,
                response,
                query,
            ) in self.irrigation_data.iterate_data():
                if query:
                    query_tasks.append(
                        self.process_query(query_type, query, query_id, response_id)
                    )

            await asyncio.gather(*query_tasks)
            await self.irrigation_data.save_data()
        except Exception as e:
            logger.exception("An error occurred during query processing.")
            raise

    async def process_query(self, query_type, query, query_id, response_id):
        if "scopus_queries" in query_type:
            output_path = await self.scopus_search.search_and_parse(
                query, query_id, response_id
            )
        elif "alex_queries" in query_type:
            output_path = await self.openalex_search.search_papers(
                query, query_id, response_id
            )
        else:
            return
        await self.irrigation_data.update_response(
            query_id, response_id, "yaml_path", str(output_path)
        )


async def main():
    yaml_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline_queries.yaml"
    output_folder = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\search_results"
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    email = "bnsoh2@huskers.unl.edu"

    query_processor = QueryProcessor(yaml_file, output_folder, api_key_path, email)
    await query_processor.process_queries()


if __name__ == "__main__":
    asyncio.run(main())
