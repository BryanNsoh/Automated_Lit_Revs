import asyncio
import logging
from pathlib import Path
from openalex_search import OpenAlexPaperSearch
from scopus_search import ScopusSearch
from yaml_iterator import IrrigationData
from web_scraper import WebScraper
from ruamel.yaml import YAML

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

# Optional: Create a file handler to log messages to a file
file_handler = logging.FileHandler("searchNscrape.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class QueryProcessor:
    def __init__(
        self, yaml_file, output_folder, api_key_path, email, checkpoint_interval=100
    ):
        self.yaml_file = yaml_file
        self.output_folder = Path(output_folder)
        self.api_key_path = api_key_path
        self.email = email
        self.web_scraper = WebScraper(
            proxies_file=r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\proxies.txt"
        )
        self.openalex_search = OpenAlexPaperSearch(
            email, self.web_scraper, self.output_folder
        )
        self.scopus_search = ScopusSearch(
            api_key_path, self.web_scraper, self.output_folder
        )
        self.irrigation_data = IrrigationData(yaml_file)
        self.checkpoint_interval = checkpoint_interval
        self.processed_queries = 0

    async def process_queries(self):
        try:
            await self.irrigation_data.load_data()
            logger.info("Loaded YAML data successfully.")

            # Start scraping
            await self.web_scraper.start_scraping()
            logger.info("Started scraping.")

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
                    logger.info(f"Adding query {query_id} to processing queue.")
                    await self.web_scraper.get_url_content(
                        query
                    )  # Add the URL to the url_queue
                    if "scopus_queries" in query_type:
                        await self.process_scopus_query(
                            point_title,
                            subsection,
                            query_type,
                            query,
                            query_id,
                            response_id,
                        )
                    elif "alex_queries" in query_type:
                        await self.process_openalex_query(
                            point_title,
                            subsection,
                            query_type,
                            query,
                            query_id,
                            response_id,
                        )
                    else:
                        logger.warning(f"Unsupported query type: {query_type}")

                    self.processed_queries += 1
                    if self.processed_queries % self.checkpoint_interval == 0:
                        logger.info(
                            f"Processed {self.processed_queries} queries. Saving checkpoint."
                        )
                        await self.irrigation_data.save_data()
                else:
                    logger.info(
                        f"Skipping query {query_id} as it already has a yaml_path."
                    )

            logger.info("Finished processing queries.")
            await self.irrigation_data.save_data()
            logger.info("Saved updated YAML data.")

        except Exception as e:
            logger.error("An error occurred during query processing.", exc_info=True)
            raise

    async def process_scopus_query(
        self, point_title, subsection, query_type, query, query_id, response_id
    ):
        try:
            logger.info(f"Processing Scopus query {query_id}.")
            content = await self.web_scraper.get_url_content(
                query
            )  # Get the scraped content
            output_path = await self.scopus_search.search_and_parse(
                query, query_id, response_id, content=content
            )
            logger.info(
                f"Processed Scopus query {query_id}. Output path: {output_path}"
            )
            await self.irrigation_data.update_response(
                subsection["index"],
                point_title,
                query_id,
                response_id,
                "yaml_path",
                str(output_path),
            )
            logger.info(
                f"Updated response for query {query_id} with yaml_path: {output_path}"
            )
        except Exception as e:
            logger.error(
                f"An error occurred while processing Scopus query {query_id}.",
                exc_info=True,
            )

    async def process_openalex_query(
        self, point_title, subsection, query_type, query, query_id, response_id
    ):
        try:
            logger.info(f"Processing OpenAlex query {query_id}.")
            content = await self.web_scraper.get_url_content(
                query
            )  # Get the scraped content
            output_path = await self.openalex_search.search_papers(
                query, query_id, response_id, content=content
            )
            logger.info(
                f"Processed OpenAlex query {query_id}. Output path: {output_path}"
            )
            await self.irrigation_data.update_response(
                subsection["index"],
                point_title,
                query_id,
                response_id,
                "yaml_path",
                str(output_path),
            )
            logger.info(
                f"Updated response for query {query_id} with yaml_path: {output_path}"
            )
        except Exception as e:
            logger.error(
                f"An error occurred while processing OpenAlex query {query_id}.",
                exc_info=True,
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

    query_processor = QueryProcessor(
        yaml_file, output_folder, api_key_path, email, checkpoint_interval=500
    )

    if delete_current_entries:
        await query_processor.delete_yaml_entries()

    await query_processor.process_queries()
    logger.info("Code execution completed successfully.")


if __name__ == "__main__":
    delete_current_entries = (
        True  # Set this to false if you dont want current entries deleted
    )
    asyncio.run(main(delete_current_entries))
