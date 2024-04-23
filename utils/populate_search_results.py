import asyncio
import logging
from pathlib import Path
from openalex_search import OpenAlexPaperSearch
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
    def __init__(
        self,
        yaml_file,
        output_folder,
        api_key_path,
        email,
        new_yaml_file,
        structured_mode=True,
    ):
        self.yaml_file = yaml_file
        self.output_folder = Path(output_folder)
        self.api_key_path = api_key_path
        self.email = email
        self.new_yaml_file = new_yaml_file
        self.web_scraper = WebScraper()
        self.openalex_search = OpenAlexPaperSearch(
            email, self.web_scraper, self.output_folder
        )
        self.scopus_search = ScopusSearch(
            api_key_path, self.web_scraper, self.output_folder
        )
        self.irrigation_data = IrrigationData(yaml_file)
        self.new_data = {}
        self.structured_mode = structured_mode

    async def process_queries(self):
        try:
            print("Loading YAML data...")
            await self.irrigation_data.load_data()
            logger.info("Loaded YAML data successfully.")

            query_tasks = []
            entries_to_process = []
            async for (
                subsection,
                point_title,
                point_content,
                query_type,
                query_id,
                response_id,
                response,
                query,
            ) in self.irrigation_data.iterate_data():
                # print subsection contents
                print(
                    f"Subsection: {subsection['index']}, Subsection Title: {subsection['subsection_title']}, Point Title: {point_title}, Point Content: {point_content}"
                )
                if query and "yaml_path" not in response:
                    entries_to_process.append(
                        (
                            subsection["index"],
                            subsection["subsection_title"],
                            point_title,
                            point_content,
                        )
                    )
                    query_tasks.append(
                        self.process_query(
                            subsection,
                            point_title,
                            point_content,
                            query_type,
                            query,
                            query_id,
                            response_id,
                        )
                    )

            logger.info(f"Found {len(entries_to_process)} entries to process:")
            for entry in entries_to_process:
                logger.info(
                    f"Subsection: {entry[0]}, Subsection Title: {entry[1]}, Point Title: {entry[2]}, Point Content: {entry[3]}"
                )

            logger.info(f"Processing {len(query_tasks)} queries.")
            await asyncio.gather(*query_tasks)
            logger.info("Finished processing queries.")

            await self.save_new_data()
            logger.info("Saved new YAML data.")

        except Exception as e:
            logger.exception("An error occurred during query processing.")
            raise

    async def process_query(
        self,
        subsection,
        point_title,
        point_content,
        query_type,
        query,
        query_id,
        response_id,
    ):
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

        await self.update_new_data(
            subsection["index"],
            subsection["subsection_title"],
            point_title,
            point_content,
            str(output_path),
        )

    async def update_new_data(
        self, subsection_index, subsection_title, point_title, point_content, yaml_path
    ):
        if subsection_index not in self.new_data:
            self.new_data[subsection_index] = {
                "subsection_title": subsection_title,
                "point_content": {},
            }
        if point_title not in self.new_data[subsection_index]["point_content"]:
            self.new_data[subsection_index]["point_content"][point_title] = {
                "content": point_content,
                "yaml_paths": [],
            }
        self.new_data[subsection_index]["point_content"][point_title][
            "yaml_paths"
        ].append(yaml_path)

        await self.save_new_data()

    async def save_new_data(self):
        yaml = YAML()
        with open(self.new_yaml_file, "w") as file:
            yaml.dump(self.new_data, file)


async def main():
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    email = "bnsoh2@huskers.unl.edu"

    # Set the mode: True for structured mode, False for free mode
    structured_mode = False

    async def process_sections():
        if structured_mode:
            for section in range(6, 9):
                yaml_file = rf"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section{section}\outline_queries.yaml"
                output_folder = rf"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section{section}\search_results"
                new_yaml_file = rf"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section{section}\new_outline_structure.yaml"

                query_processor = QueryProcessor(
                    yaml_file,
                    output_folder,
                    api_key_path,
                    email,
                    new_yaml_file,
                    structured_mode,
                )
                await query_processor.process_queries()
        else:
            yaml_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\investigations\outline_queries.yaml"
            output_folder = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\investigations\search_results"
            new_yaml_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\investigations\new_outline_structure.yaml"

            query_processor = QueryProcessor(
                yaml_file,
                output_folder,
                api_key_path,
                email,
                new_yaml_file,
                structured_mode,
            )
            await query_processor.process_queries()

    await process_sections()

    logger.info("Code execution completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
