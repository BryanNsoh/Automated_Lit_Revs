import os
import yaml
import logging
from prompts import (
    review_intention,
    section_intentions,
    previous_sections,
    write_next_section,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("summary_generator.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class SummaryGenerator:
    def __init__(self, processed_data_path):
        self.processed_data_path = processed_data_path

    def generate_summary(self, section_number, outline_data):
        summary_content = ""

        summary_content += "<instructions>\n"
        summary_content += f"{write_next_section}\n"
        summary_content += "</instructions>\n\n"

        summary_content += "<documents>\n"

        summary_content += "<review_intention>\n"
        summary_content += f"{review_intention}\n"
        summary_content += "</review_intention>\n\n"

        summary_content += "<section_intention>\n"
        section_intention = section_intentions.get(section_number, "")
        summary_content += f"{section_intention}\n"
        summary_content += "</section_intention>\n\n"

        for subsection_number, subsection_data in outline_data.items():
            subsection_title = subsection_data.get("subsection_title", "")
            point_content_data = subsection_data.get("point_content", {})

            subsection_folder = os.path.join(
                self.processed_data_path,
                f"section{section_number}",
                "processed",
                f"subsection_{subsection_number}",
            )

            if not os.path.exists(subsection_folder):
                logger.error(f"Subsection folder not found: {subsection_folder}")
                continue

            summary_content += "<subsection_title>\n"
            summary_content += f"{subsection_title}\n"
            print(subsection_title)
            summary_content += "</subsection_title>\n\n"

            for point_number, point_data in point_content_data.items():
                point_content = point_data.get("content", "")
                point_folder_name = f"point_{point_number.lower().replace(' ', '_')}"
                point_folder_path = os.path.join(subsection_folder, point_folder_name)

                parsed_entries_file = os.path.join(
                    point_folder_path, "relevant_entries_parsed.yaml"
                )
                if os.path.exists(parsed_entries_file):
                    with open(parsed_entries_file, "r", encoding="utf-8") as file:
                        parsed_entries = yaml.safe_load(file)
                else:
                    logger.warning(
                        f"Parsed entries file not found: {parsed_entries_file}"
                    )
                    continue

                # Sort parsed_entries by relevance_score in descending order
                sorted_entries = sorted(
                    parsed_entries,
                    key=lambda x: float(x.get("relevance_score", 0)),
                    reverse=True,
                )

                # Take the top 5 entries
                top_entries = sorted_entries[:5]

                summary_content += f"<subsection_point_{point_number}>\n"
                summary_content += f"Point: {point_content}\n\n"
                summary_content += "Papers to support point:\n\n"

                for entry_index, entry in enumerate(top_entries, start=1):
                    summary_content += f"Paper {entry_index}:\n"
                    summary_content += (
                        f"- APA Citation: {entry.get('apa_citation', '')}\n"
                    )
                    summary_content += (
                        f"  Main Objective: {entry.get('main_objective', '')}\n"
                    )
                    summary_content += (
                        f"  Study Location: {entry.get('study_location', '')}\n"
                    )
                    summary_content += (
                        f"  Data Sources: {entry.get('data_sources', '')}\n"
                    )
                    summary_content += (
                        f"  Technologies Used: {entry.get('technologies_used', '')}\n"
                    )
                    summary_content += (
                        f"  Key Findings: {entry.get('key_findings', '')}\n"
                    )
                    summary_content += f"  Extract 1: {entry.get('extract_1', '')}\n"
                    summary_content += f"  Extract 2: {entry.get('extract_2', '')}\n"
                    summary_content += (
                        f"  Limitations: {entry.get('limitations', '')}\n"
                    )
                    summary_content += f"  Relevance Evaluation: {entry.get('relevance_evaluation', '')}\n"
                    summary_content += (
                        f"  Relevance Score: {entry.get('relevance_score', '')}\n"
                    )
                    summary_content += (
                        f"  Inline Citation: {entry.get('inline_citation', '')}\n"
                    )
                    summary_content += (
                        f"  Explanation: {entry.get('explanation', '')}\n\n"
                    )

                summary_content += f"</subsection_point_{point_number}>\n\n"

                summary_content += "<previous_sections>\n"
                summary_content += f"{previous_sections}\n"
                summary_content += "</previous_sections>\n\n"

                summary_content += "</documents>\n"

                summary_content += "<instructions>\n"
                summary_content += f"{write_next_section}\n"
                summary_content += "</instructions>\n\n"

            summary_file = os.path.join(subsection_folder, "summary.txt")
            with open(summary_file, "w", encoding="utf-8") as file:
                file.write(summary_content)

            logger.info(f"Summary file generated: {summary_file}")


def main():
    processed_data_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents"
    section_number = "3"

    outline_file_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\new_outline_structure.yaml"

    with open(outline_file_path, "r", encoding="utf-8") as file:
        outline_data = yaml.safe_load(file)

    summary_generator = SummaryGenerator(processed_data_path)
    summary_generator.generate_summary(section_number, outline_data)


if __name__ == "__main__":
    main()
