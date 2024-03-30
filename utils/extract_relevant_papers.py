import os
import asyncio
import aiofiles
import yaml
import logging
import json
from llm_api_handler import LLM_APIHandler
from prompts import (
    get_prompt,
    review_intention,
    section_intentions,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
file_handler = logging.FileHandler("paper_ranker.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class MetricsTracker:
    def __init__(self):
        self.total_entries_processed = 0
        self.duplicate_entries = 0
        self.relevant_entries = 0

    def increment_total_entries_processed(self):
        self.total_entries_processed += 1

    def increment_duplicate_entries(self):
        self.duplicate_entries += 1

    def increment_relevant_entries(self):
        self.relevant_entries += 1

    def log_metrics(self):
        logger.info(f"Metrics Summary:")
        logger.info(f"- Total entries processed: {self.total_entries_processed}")
        logger.info(f"- Duplicate entries skipped: {self.duplicate_entries}")
        logger.info(f"- Relevant entries found: {self.relevant_entries}")


class PaperRanker:
    def __init__(self, api_key_path, max_retries=10):
        self.llm_api_handler = LLM_APIHandler(api_key_path)
        self.max_retries = max_retries
        self.metrics_tracker = MetricsTracker()
        self.processed_dois = set()
        self.processed_titles = set()

    async def process_yaml_entry(
        self, entry, subsection_title, point_content, section_intention
    ):
        self.metrics_tracker.increment_total_entries_processed()

        # Check for duplicate entry
        doi = entry.get("doi", "")
        title = entry.get("title", "")
        if doi:
            if doi in self.processed_dois:
                self.metrics_tracker.increment_duplicate_entries()
                logger.debug(f"Skipping duplicate entry with DOI: {doi}")
                return None
            self.processed_dois.add(doi)
        elif title:
            if title in self.processed_titles:
                self.metrics_tracker.increment_duplicate_entries()
                logger.debug(f"Skipping duplicate entry with title: {title}")
                return None
            self.processed_titles.add(title)
        else:
            logger.warning(f"Entry has neither DOI nor title. Skipping.")
            return None

        retry_count = 0
        while retry_count < self.max_retries:
            prompt = get_prompt(
                "rank_papers",
                review_intention=review_intention,
                point_content=point_content,
                subsection_title=subsection_title,
                document_title=entry.get("title", ""),
                full_text=entry.get("full_text", ""),
                abstract=entry.get("description", ""),
                section_intention=section_intention,
            )
            # Report if the prompt is empty string
            if not prompt:
                logger.warning(f"Empty prompt generated for entry: {doi or title}")
                print(prompt)

            response = await self.llm_api_handler.generate_gemini_content(prompt)

            try:
                json_data = json.loads(response)
                expected_keys = [
                    "analysis",
                    "verbatim_quote1",
                    "verbatim_quote2",
                    "verbatim_quote3",
                    "limitations",
                ]
                missing_keys = set(expected_keys) - set(json_data.keys())
                if not missing_keys:
                    # Assign first "relevance_score*" key to "relevance_score1"
                    relevance_score_keys = [
                        k for k in json_data.keys() if k.startswith("relevance_score")
                    ]
                    if relevance_score_keys:
                        json_data["relevance_score1"] = json_data[
                            relevance_score_keys[0]
                        ]
                    else:
                        logger.warning(
                            f"No relevance score found for entry: {doi or title}"
                        )

                    entry.update(json_data)
                    logger.debug(f"Successfully processed entry: {doi or title}")
                    break
                else:
                    logger.warning(
                        f"The following keys are missing in the response: {missing_keys}"
                    )
                    logger.debug(f"Missing keys: {missing_keys}")
                    retry_count += 1
            except json.JSONDecodeError:
                logger.warning(
                    f"Invalid JSON response for entry: {doi or title}. Retrying..."
                )
                print("Invalid JSON response:")
                print(response)
                retry_count += 1

            if retry_count == self.max_retries:
                logger.error(
                    f"Max retries reached for entry: {doi or title}. Skipping entry."
                )

        return entry

    async def process_yaml_files(
        self,
        input_folder_path,
        output_folder_path,
        subsection_title,
        point_content,
        section_intention,
    ):
        processed_files = 0
        async for file_path in self.get_yaml_files(input_folder_path):
            logger.info(f"Processing file: {file_path}")
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(await file.read())
            relevant_entries = []
            for entry in data:
                processed_entry = await self.process_yaml_entry(
                    entry, subsection_title, point_content, section_intention
                )
                if processed_entry and processed_entry.get("relevance_score1", 0) > 5:
                    relevant_entries.append(processed_entry)
                    self.metrics_tracker.increment_relevant_entries()
            if relevant_entries:
                output_file_path = os.path.join(
                    output_folder_path, os.path.basename(file_path)
                )
                async with aiofiles.open(output_file_path, "w") as file:
                    await file.write(yaml.dump(relevant_entries))
                logger.info(
                    f"Saved {len(relevant_entries)} relevant entries to: {output_file_path}"
                )
            else:
                logger.info(f"No relevant entries found in file: {file_path}")
            processed_files += 1
        logger.info(f"Processed {processed_files} YAML files")

    async def get_yaml_files(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    yield os.path.join(root, file)


class FileSystemHandler:
    async def process_outline(
        self,
        input_folder_path,
        output_folder_path,
        ranker,
        outline_file_path,
        section_number,
    ):
        await self.delete_empty_yaml_files(input_folder_path)
        async with aiofiles.open(outline_file_path, "r", encoding="utf-8") as file:
            outline_data = yaml.safe_load(await file.read())
        tasks = []
        for subsection in outline_data["subsections"]:
            subsection_index = subsection["index"]
            subsection_title = subsection["subsection_title"]
            subsection_folder = os.path.join(
                output_folder_path, f"subsection_{subsection_index}"
            )
            os.makedirs(subsection_folder, exist_ok=True)
            for point_dict in subsection["points"]:
                for point_key, point in point_dict.items():
                    point_content = point["point_content"]
                    point_folder_name = point_key.replace(" ", "_")
                    point_folder = os.path.join(subsection_folder, point_folder_name)
                    os.makedirs(point_folder, exist_ok=True)
                    if str(subsection_index) == section_number:
                        section_intention = section_intentions.get(section_number, "")
                        task = asyncio.create_task(
                            ranker.process_yaml_files(
                                input_folder_path,
                                point_folder,
                                subsection_title,
                                point_content,
                                section_intention,
                            )
                        )
                        tasks.append(task)
        await asyncio.gather(*tasks)

    async def delete_empty_yaml_files(self, folder_path):
        deleted_files = 0
        async for file_path in self.get_yaml_files(folder_path):
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                    content = await file.read()
                    if content.strip() == "[]":
                        logger.info(f"Deleting empty YAML file: {file_path}")
                        await file.close()  # Close the file before deleting
                        await asyncio.sleep(1)  # Add a small delay
                        os.remove(file_path)
                        deleted_files += 1
            except PermissionError as e:
                logger.warning(f"Failed to delete file: {file_path}. Error: {str(e)}")
        logger.info(f"Deleted {deleted_files} empty YAML files")

    async def get_yaml_files(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    yield os.path.join(root, file)


async def main(section_number):
    input_folder_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\raw"
    output_folder_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\processed"
    outline_file_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\research_paper_outline.yaml"
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"

    ranker = PaperRanker(api_key_path)
    file_system_handler = FileSystemHandler()
    os.makedirs(output_folder_path, exist_ok=True)
    logger.info(f"Starting paper ranking process for section {section_number}...")
    await file_system_handler.process_outline(
        input_folder_path, output_folder_path, ranker, outline_file_path, section_number
    )
    logger.info(f"Paper ranking process completed for section {section_number}.")
    # Log the metrics at the end
    try:
        ranker.metrics_tracker.log_metrics()
    except Exception as e:
        logger.exception("Error logging metrics:")
        pass


if __name__ == "__main__":
    section_number = "3"  # Replace with the desired section number
    asyncio.run(main(section_number))
