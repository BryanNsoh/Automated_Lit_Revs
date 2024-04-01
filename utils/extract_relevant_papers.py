import asyncio
import aiofiles
import yaml
import logging
import json
import re
import os
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

    def increment_relevant_entries(self, count):
        self.relevant_entries += count

    def log_metrics(self):
        logger.info(f"Metrics Summary:")
        logger.info(f"- Total entries processed: {self.total_entries_processed}")
        logger.info(f"- Relevant entries found: {self.relevant_entries}")


class PaperRanker:
    def __init__(self, api_key_path, max_retries=4):
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
            response = await self.llm_api_handler.generate_gemini_content(prompt)
            if response is None:
                logger.warning(
                    "Received None response from the Gemini API. Skipping entry."
                )
                return None
            response = re.search(r"\{.*\}", response, re.DOTALL)
            if response:
                response = response.group()
            else:
                response = ""
            print(response)
            try:
                json_data = json.loads(response)
                if "relevance_score" in json_data:
                    try:
                        relevance_score = float(json_data["relevance_score"])
                        if relevance_score < 0 or relevance_score > 1:
                            raise ValueError("Relevance score must be between 0 and 1")
                        entry.update(json_data)
                        logger.debug(f"Successfully processed entry.")
                        return entry
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Invalid relevance score for current entry. Retrying..."
                        )
                        retry_count += 1
                else:
                    logger.warning(
                        f"Relevance score not found in the response. Retrying..."
                    )
                    retry_count += 1
            except json.JSONDecodeError:
                logger.warning(
                    f"Invalid JSON response for the current entry. Retrying immediately..."
                )
                retry_count += 1

        logger.error(f"Max retries reached for current entry. Skipping entry.")
        return None

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
        progress_file_path,
    ):
        self.output_folder_path = output_folder_path
        processed_files = 0
        progress_data = await self.load_progress(progress_file_path)
        async for file_path in self.get_yaml_files(input_folder_path):
            if file_path in progress_data["processed_files"]:
                continue
            logger.info(f"Processing file: {file_path}")
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(await file.read())
            tasks = []
            for entry in data:
                task = asyncio.create_task(
                    self.process_yaml_entry(
                        entry, subsection_title, point_content, section_intention
                    )
                )
                tasks.append(task)
            processed_entries = await asyncio.gather(*tasks)
            relevant_entries = [
                entry
                for entry in processed_entries
                if entry and float(entry.get("relevance_score", 0)) > 0.5
            ]
            if relevant_entries:
                await self.save_relevant_entries(file_path, relevant_entries)
                logger.info(f"Successfully processed file: {file_path}")
                self.metrics_tracker.increment_relevant_entries(len(relevant_entries))
            else:
                logger.info(f"No relevant entries found in file: {file_path}")
            processed_files += 1
            progress_data["processed_files"].append(file_path)
            await self.save_progress(progress_file_path, progress_data)
        logger.info(f"Processed {processed_files} YAML files")

    async def load_progress(self, progress_file_path):
        if os.path.exists(progress_file_path):
            async with aiofiles.open(progress_file_path, "r", encoding="utf-8") as file:
                progress_data = yaml.safe_load(await file.read())
                return progress_data or {"processed_files": []}
        return {"processed_files": []}

    async def save_progress(self, progress_file_path, progress_data):
        async with aiofiles.open(progress_file_path, "w", encoding="utf-8") as file:
            await file.write(yaml.safe_dump(progress_data, allow_unicode=True))

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
                    progress_file_path = os.path.join(point_folder, self.progress_file)
                    await ranker.process_yaml_files(
                        input_folder_path,
                        point_folder,
                        subsection_title,
                        point_content,
                        section_intention,
                        progress_file_path,
                    )

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
    async with LLM_APIHandler(api_key_path) as api_handler:
        ranker = PaperRanker(api_key_path)
        file_system_handler = FileSystemHandler()
        os.makedirs(output_folder_path, exist_ok=True)
        logger.info(f"Starting paper ranking process for section {section_number}...")
        await file_system_handler.process_outline(
            input_folder_path,
            output_folder_path,
            ranker,
            outline_file_path,
            section_number,
        )
        logger.info(f"Paper ranking process completed for section {section_number}.")
        try:
            ranker.metrics_tracker.log_metrics()
        except Exception as e:
            logger.exception("Error logging metrics:")
            pass


if __name__ == "__main__":
    section_number = "3"  # Replace with the desired section number
    asyncio.run(main(section_number))
