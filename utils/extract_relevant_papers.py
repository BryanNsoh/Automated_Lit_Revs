import os
import asyncio
import aiofiles
import yaml
import logging
import json
import re
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
        self.relevant_entries = 0

    def increment_total_entries_processed(self):
        self.total_entries_processed += 1

    def increment_relevant_entries(self):
        self.relevant_entries += 1

    def log_metrics(self):
        logger.info(f"Metrics Summary:")
        logger.info(f"- Total entries processed: {self.total_entries_processed}")
        logger.info(f"- Relevant entries found: {self.relevant_entries}")


class PaperRanker:
    def __init__(self, api_key_path, max_retries=10):
        self.llm_api_handler = LLM_APIHandler(api_key_path)
        self.max_retries = max_retries
        self.metrics_tracker = MetricsTracker()

    async def process_yaml_entry(
        self, entry, subsection_title, point_content, section_intention
    ):
        self.metrics_tracker.increment_total_entries_processed()

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
                logger.warning(f"Empty prompt generated for entry: {entry}")
                print(prompt)

            response = await self.llm_api_handler.generate_gemini_content(prompt)
            # remove anything not between { and } in the response
            response = re.search(r"\{.*\}", response, re.DOTALL)
            if response:
                response = response.group()
            else:
                response = ""

            print(response)

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
                        relevance_score = json_data[relevance_score_keys[0]]
                        try:
                            relevance_score = float(relevance_score)
                            if relevance_score < 0 or relevance_score > 1:
                                raise ValueError(
                                    "Relevance score must be between 0 and 1"
                                )
                            json_data["relevance_score1"] = relevance_score
                            break
                        except (ValueError, TypeError):
                            logger.warning(
                                f"Invalid relevance score for current entry. Retrying..."
                            )
                            retry_count += 1
                    else:
                        logger.warning(f"No relevance score found for current entry")
                        retry_count += 1
                else:
                    logger.warning(
                        f"The following keys are missing in the response: {missing_keys}"
                    )
                    logger.debug(f"Missing keys: {missing_keys}")
                    retry_count += 1
            except json.JSONDecodeError:
                logger.warning(
                    f"Invalid JSON response for entry current entry. Retrying..."
                )
                retry_count += 1

            if retry_count == self.max_retries:
                logger.error(f"Max retries reached for current entry. Skipping entry.")
                return None

        entry.update(json_data)
        logger.debug(f"Successfully processed entry for current entry")
        return entry

    async def save_relevant_entries(self, input_file_path, relevant_entries):
        input_file_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_name = f"{input_file_name}_processed.yaml"
        output_file_path = os.path.join(self.output_folder_path, output_file_name)
        async with aiofiles.open(output_file_path, "w", encoding="utf-8") as file:
            await file.write(yaml.safe_dump(relevant_entries, allow_unicode=True))
        logger.info(f"Successfully processed and saved file: {output_file_path}")

    async def process_yaml_files(
        self,
        input_folder_path,
        output_folder_path,
        subsection_title,
        point_content,
        section_intention,
        batch_size=None,
    ):
        self.output_folder_path = output_folder_path
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
                try:
                    if (
                        processed_entry
                        and float(processed_entry.get("relevance_score1", 0)) > 0.5
                    ):
                        relevant_entries.append(processed_entry)
                        self.metrics_tracker.increment_relevant_entries()
                except ValueError:
                    logger.warning(
                        f"Invalid relevance score for entry: {processed_entry}"
                    )
            if relevant_entries:
                await self.save_relevant_entries(file_path, relevant_entries)
                logger.info(f"Successfully processed file: {file_path}")
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
    def __init__(self):
        self.progress_file = "progress.yaml"

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
        section_intention = section_intentions.get(section_number, "")

        progress_data = await self.load_progress()

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

                    if self.is_point_processed(
                        progress_data, subsection_index, point_key
                    ):
                        logger.info(f"Skipping already processed point: {point_key}")
                        continue

                    await ranker.process_yaml_files(
                        input_folder_path,
                        point_folder,
                        subsection_title,
                        point_content,
                        section_intention,
                    )

                    progress_data = self.mark_point_processed(
                        progress_data, subsection_index, point_key
                    )
                    await self.save_progress(progress_data)

    def is_point_processed(self, progress_data, subsection_index, point_key):
        subsection_key = f"subsection_{subsection_index}"
        if subsection_key in progress_data:
            return point_key in progress_data[subsection_key]
        return False

    def mark_point_processed(self, progress_data, subsection_index, point_key):
        subsection_key = f"subsection_{subsection_index}"
        if subsection_key not in progress_data:
            progress_data[subsection_key] = []
        progress_data[subsection_key].append(point_key)
        return progress_data

    async def load_progress(self):
        if os.path.exists(self.progress_file):
            async with aiofiles.open(self.progress_file, "r", encoding="utf-8") as file:
                progress_data = yaml.safe_load(await file.read())
                return progress_data or {}
        return {}

    async def save_progress(self, progress_data):
        async with aiofiles.open(self.progress_file, "w", encoding="utf-8") as file:
            await file.write(yaml.safe_dump(progress_data, allow_unicode=True))

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
