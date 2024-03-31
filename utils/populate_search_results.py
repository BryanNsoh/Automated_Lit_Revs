import asyncio
import logging
from pathlib import Path
from previous_work.openalex_search import OpenAlexPaperSearch
from scopus_search import ScopusSearch
from yaml_iterator import IrrigationData
from web_scraper import WebScraper
from ruamel.yaml import YAML

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create a file handler to log messages to a file
file_handler = logging.FileHandler("get_results.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)


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
            await self.irrigation_data.load_data()
            logger.info("Loaded YAML data successfully.")

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
                if query and "yaml_path" not in response:
                    query_tasks.append(
                        self.process_query(query_type, query, query_id, response_id)
                    )
                else:
                    logger.info(
                        f"Skipping query {query_id} as it already has a yaml_path."
                    )

            logger.info(f"Processing {len(query_tasks)} queries.")
            await asyncio.gather(*query_tasks)
            logger.info("Finished processing queries.")

            await self.irrigation_data.save_data()
            logger.info("Saved updated YAML data.")

        except Exception as e:
            logger.exception("An error occurred during query processing.")
            raise

    async def process_query(self, query_type, query, query_id, response_id):
        if "scopus_queries" in query_type:
            output_path = await self.scopus_search.search_and_parse(
                query, query_id, response_id
            )
            logger.info(
                f"Processed Scopus query {query_id}. Output path: {output_path}"
            )
        elif "alex_queries" in query_type:
            output_path = await self.openalex_search.search_papers(
                query, query_id, response_id
            )
            logger.info(
                f"Processed OpenAlex query {query_id}. Output path: {output_path}"
            )
        else:
            logger.warning(f"Unsupported query type: {query_type}")
            return

        await self.irrigation_data.update_response(
            query_id, response_id, "yaml_path", str(output_path)
        )

    async def delete_yaml_entries(self):
        yaml = YAML()
        with open(self.yaml_file, "r") as file:
            data = yaml.load(file)

        def remove_yaml_path(obj):
            if isinstance(obj, dict):
                if "yaml_path" in obj:
                    del obj["yaml_path"]
                for value in obj.values():
                    remove_yaml_path(value)
            elif isinstance(obj, list):
                for item in obj:
                    remove_yaml_path(item)

        remove_yaml_path(data)

        with open(self.yaml_file, "w") as file:
            yaml.dump(data, file)

        logger.info("Deleted all 'yaml_path' keys and values.")


async def main(delete_current_entries: bool):
    yaml_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline_queries.yaml"
    output_folder = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\search_results"
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    email = "bnsoh2@huskers.unl.edu"

    query_processor = QueryProcessor(yaml_file, output_folder, api_key_path, email)

    if delete_current_entries:
        await query_processor.delete_yaml_entries()

    await query_processor.process_queries()
    logger.info("Code execution completed successfully.")


if __name__ == "__main__":
    delete_current_entries = (
        False  # Set this to false if you dont want current entries deleted
    )
    asyncio.run(main(delete_current_entries))
