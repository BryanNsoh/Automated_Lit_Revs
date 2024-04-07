import asyncio
import aiofiles
import yaml
import logging
import json
import chardet
import re
import os
from llm_api_handler import LLM_APIHandler
from prompts import get_prompt, review_intention, section_intentions

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
        self,
        entry,
        subsection_title,
        point_content,
        section_intention,
        output_folder_path,
    ):
        self.metrics_tracker.increment_total_entries_processed()
        retry_count = 0
        while retry_count < self.max_retries:
            prompt = get_prompt(
                template_name="rank_papers",
                review_intention=review_intention,
                point_content=point_content,
                subsection_title=subsection_title,
                full_text=entry.get("full_text", ""),
                section_intention=section_intention,
            )
            try:
                print(f"Processing entry: {entry.get('title', '')}")
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
                try:
                    json_data = json.loads(response)
                    if "relevance_score" in json_data:
                        try:
                            relevance_score = float(json_data["relevance_score"])
                            if relevance_score < 0 or relevance_score > 1:
                                raise ValueError(
                                    "Relevance score must be between 0 and 1"
                                )
                            entry.update(json_data)
                            logger.debug(f"Successfully processed entry.")
                            if relevance_score > 0.5:
                                await self.save_relevant_entry(
                                    output_folder_path, entry
                                )
                                await self.save_parsed_entry(
                                    output_folder_path, json_data
                                )
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
            except Exception as e:
                logger.exception(f"Error processing entry: {str(e)}")
                retry_count += 1

        logger.error(f"Max retries reached for current entry. Skipping entry.")
        return None

    async def save_relevant_entry(self, output_folder_path, entry):
        output_file_name = "relevant_entries_all.yaml"
        output_file_path = os.path.join(output_folder_path, output_file_name)
        try:
            async with aiofiles.open(output_file_path, "a", encoding="utf-8") as file:
                yaml_data = yaml.safe_dump([entry], allow_unicode=True)
                await file.write(yaml_data)
            logger.info(f"Successfully saved relevant entry to: {output_file_path}")
        except Exception as e:
            logger.exception(f"Error saving relevant entry: {str(e)}")

    async def save_parsed_entry(self, output_folder_path, parsed_data):
        output_file_name = "relevant_entries_parsed.yaml"
        output_file_path = os.path.join(output_folder_path, output_file_name)
        try:
            async with aiofiles.open(output_file_path, "a", encoding="utf-8") as file:
                yaml_data = yaml.safe_dump([parsed_data], allow_unicode=True)
                await file.write(yaml_data)
            logger.info(f"Successfully saved parsed entry to: {output_file_path}")
        except Exception as e:
            logger.exception(f"Error saving parsed entry: {str(e)}")

    async def process_yaml_files(
        self,
        yaml_file_paths,
        output_folder_path,
        subsection_title,
        point_content,
        section_intention,
    ):
        tasks = []
        for yaml_file_path in yaml_file_paths:
            try:
                async with aiofiles.open(yaml_file_path, "r", encoding="utf-8") as file:
                    data = yaml.safe_load(await file.read())
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.exception(f"Error loading YAML file: {str(e)}")
                continue
            for entry in data:
                task = asyncio.create_task(
                    self.process_yaml_entry(
                        entry,
                        subsection_title,
                        point_content,
                        section_intention,
                        output_folder_path,
                    )
                )
                tasks.append(task)
        processed_entries = await asyncio.gather(*tasks, return_exceptions=True)
        relevant_entries = [
            entry
            for entry in processed_entries
            if entry
            and isinstance(entry, dict)
            and float(entry.get("relevance_score", 0)) > 0.5
        ]
        self.metrics_tracker.increment_relevant_entries(len(relevant_entries))
        logger.info(f"Successfully processed files.")


class FileSystemHandler:
    def __init__(self):
        self.progress_file = "progress.yaml"

    async def process_outline(
        self,
        outline_file_path,
        output_folder_path,
        ranker,
        section_number,
    ):
        try:
            async with aiofiles.open(outline_file_path, "rb") as file:
                content = await file.read()
                encoding = chardet.detect(content)["encoding"]
                content = content.decode(encoding, errors="replace")
                outline_data = yaml.safe_load(content)
        except FileNotFoundError:
            logger.error(f"Outline file not found: {outline_file_path}")
            return
        except Exception as e:
            logger.exception(f"Error loading outline file: {str(e)}")
            return

        section_intention = section_intentions.get(section_number, "")
        tasks = []

        for subsection_number, subsection_data in outline_data.items():
            subsection_title = subsection_data.get("subsection_title", "")
            point_content_data = subsection_data.get("point_content", {})

            subsection_folder_name = f"subsection_{subsection_number}"
            subsection_folder = os.path.join(
                output_folder_path,
                subsection_folder_name,
            )
            os.makedirs(subsection_folder, exist_ok=True)

            for point_number, point_data in point_content_data.items():
                point_content = point_data.get("content", "")
                yaml_file_paths = point_data.get("yaml_paths", [])

                point_folder_name = f"point_{point_number.lower().replace(' ', '_')}"
                point_folder = os.path.join(
                    subsection_folder,
                    point_folder_name,
                )
                os.makedirs(point_folder, exist_ok=True)

                task = asyncio.create_task(
                    ranker.process_yaml_files(
                        yaml_file_paths,
                        point_folder,
                        subsection_title,
                        point_content,
                        section_intention,
                    )
                )
                tasks.append(task)

        await asyncio.gather(*tasks)


async def main(section_number):
    output_folder_path = rf"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section{section_number}\processed"
    outline_file_path = rf"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section{section_number}\new_outline_structure.yaml"
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    async with LLM_APIHandler(api_key_path) as api_handler:
        ranker = PaperRanker(api_key_path)
        file_system_handler = FileSystemHandler()
        os.makedirs(output_folder_path, exist_ok=True)
        logger.info(f"Starting paper ranking process for section {section_number}...")
        await file_system_handler.process_outline(6
            outline_file_path,
            output_folder_path,
            ranker,
            section_number,
        )
        logger.info(f"Paper ranking process completed for section {section_number}.")
        try:
            ranker.metrics_tracker.log_metrics()
        except Exception as e:
            logger.exception("Error logging metrics:")
            pass


if __name__ == "__main__":
    section_number = input("Enter section number: ")
    asyncio.run(main(section_number))
