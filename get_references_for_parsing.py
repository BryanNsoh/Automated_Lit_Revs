import yaml
import os
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_yaml_entries(data):
    processed_data = []
    for entry in data:
        try:
            processed_entry = {
                "doi": (
                    f"https://doi.org/{entry['doi']}"
                    if "doi" in entry
                    and not entry["doi"].startswith("https://doi.org/")
                    else entry.get("doi", None)
                ),
                "title": entry.get("title"),
                "authors": entry.get("authors"),
                "inline_citation": entry.get(
                    "inline_citation"
                ),  # Preserve existing inline citations if available
            }
            processed_data.append(processed_entry)
        except Exception as e:
            logging.error(f"Error processing entry: {entry}. Error: {e}")
    return processed_data


def process_directory(root_directory):
    all_processed_entries = []

    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            # Check if file is named 'relevant_entries_all.yaml'
            if filename == "relevant_entries_all.yaml":
                file_path = os.path.join(dirpath, filename)
                try:
                    logging.info(f"Processing file: {file_path}")
                    with open(file_path, "r", encoding="utf-8") as file:
                        yaml_data = yaml.safe_load(file)
                        processed_entries = process_yaml_entries(yaml_data)
                        all_processed_entries.extend(processed_entries)
                except Exception as e:
                    logging.error(f"Failed to process file {file_path}. Error: {e}")

    # Save the processed data to a new YAML file
    output_path = os.path.join(root_directory, "combined_processed_entries.yaml")
    try:
        logging.info(f"Writing combined output to {output_path}")
        with open(output_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(all_processed_entries, file)
    except Exception as e:
        logging.error(f"Failed to write to {output_path}. Error: {e}")


# Example usage
root_directory = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\processed"
process_directory(root_directory)
