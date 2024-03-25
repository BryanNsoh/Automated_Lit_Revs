import asyncio
import json
import logging
from hashlib import sha256
from pathlib import Path

import aiofiles

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
        self.openalex_search = OpenAlexPaperSearch(email, self.web_scraper)
        self.scopus_search = ScopusSearch(api_key_path, self.web_scraper)
        self.irrigation_data = IrrigationData(yaml_file)

    async def process_queries(self):
        try:
            await self.irrigation_data.load_data()
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
            search_results = await self.scopus_search.search_and_parse(query)
        elif "alex_queries" in query_type:
            search_results = await self.openalex_search.search_papers(query)
        else:
            return

        hashed_filename = self.get_hashed_filename(query, query_id, response_id)
        output_path = await self.save_json(search_results, hashed_filename)
        await self.irrigation_data.update_response(
            query_id, response_id, "json_path", str(output_path)
        )

    def get_hashed_filename(self, query, query_id, response_id):
        hash_input = f"{query}_{query_id}_{response_id}"
        hashed_filename = sha256(hash_input.encode()).hexdigest()
        return f"{hashed_filename}.json"

    async def save_json(self, data, filename):
        # Ensure the output directory exists
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # Create the full output path
        output_path = self.output_folder / filename

        # Save the data to a JSON file
        async with aiofiles.open(output_path, "w") as file:
            await file.write(
                json.dumps(data, indent=4)
            )  # Adding indent for pretty printing
        return output_path


async def main():
    yaml_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline_queries.yaml"
    output_folder = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\search_results"
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    email = "bnsoh2@huskers.unl.edu"

    query_processor = QueryProcessor(yaml_file, output_folder, api_key_path, email)
    await query_processor.process_queries()


if __name__ == "__main__":
    asyncio.run(main())
