import aiohttp
import asyncio
import json
import time
import logging
import yaml
from hashlib import sha256

from collections import deque
from misc_utils import prepare_text_for_json

# Create a logger
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
file_handler = logging.FileHandler("scopus.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class ScopusSearch:
    def __init__(self, key_path, doi_scraper, output_folder):
        self.load_api_keys(key_path)
        self.base_url = "http://api.elsevier.com/content/search/scopus"
        self.request_times = deque(maxlen=6)
        self.scraper = doi_scraper
        self.output_folder = output_folder

    def load_api_keys(self, key_path):
        try:
            with open(key_path, "r") as file:
                api_keys = json.load(file)
            self.api_key = api_keys["SCOPUS_API_KEY"]
            logger.info("API keys loaded successfully.")
        except FileNotFoundError:
            logger.error(f"API key file not found at path: {key_path}")
        except KeyError:
            logger.error("SCOPUS_API_KEY not found in the API key file.")
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in the API key file.")

    async def search(
        self, query, count=25, view="COMPLETE", response_format="json", max_retries=4
    ):
        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": (
                "application/json"
                if response_format == "json"
                else "application/atom+xml"
            ),
        }

        params = {"query": query.replace("\\", ""), "count": count, "view": view}

        retry_count = 0
        while retry_count < max_retries:
            try:
                # Ensure compliance with the rate limit
                while True:
                    current_time = time.time()
                    if (
                        not self.request_times
                        or current_time - self.request_times[0] >= 1
                    ):
                        self.request_times.append(current_time)
                        break
                    else:
                        await asyncio.sleep(0.2)

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.base_url, headers=headers, params=params
                    ) as response:
                        if response.status == 200:
                            logger.info("Scopus API request successful.")
                            if response_format == "json":
                                return await response.json()
                            else:
                                return await response.text()
                        else:
                            logger.warning(
                                f"Scopus API request failed with status code: {response.status}"
                            )
                            return None
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                retry_count += 1
                wait_time = 2**retry_count
                logger.warning(
                    f"Error occurred while making Scopus API request: {e}. Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})"
                )
                await asyncio.sleep(wait_time)  # Exponential backoff

        logger.error(
            f"Max retries ({max_retries}) exceeded. Unable to fetch data from the Scopus API for query: {query}"
        )
        return None

    async def search_and_parse(
        self, query, query_id, response_id, count=25, view="COMPLETE"
    ):
        try:
            results = await self.search(query, count, view, response_format="json")

            if (
                results is None
                or "search-results" not in results
                or "entry" not in results["search-results"]
            ):
                logger.warning(f"No results found for query: {query}")
                return ""
            else:
                parsed_results = []
                for entry in results["search-results"]["entry"]:
                    title = entry.get("dc:title")
                    doi = entry.get("prism:doi")
                    description = entry.get("dc:description")
                    journal = entry.get("prism:publicationName")
                    citation_count = entry.get("citedby-count", "0")
                    authors = [
                        author.get("authname")
                        for author in entry.get("author", [])
                        if author.get("authname") is not None
                    ]

                    full_text = None
                    if doi:
                        logger.info(f"Scraping full text for DOI: {doi}")
                        try:
                            full_text = await self.scraper.get_url_content(doi)
                            full_text = await prepare_text_for_json(full_text)
                            logger.info(
                                f"Full text scraped successfully for DOI: {doi}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Error occurred while scraping full text for DOI: {doi}. Error: {e}"
                            )
                    if title is not None:
                        parsed_results.append(
                            {
                                "title": title,
                                "doi": doi,
                                "description": description,
                                "journal": journal,
                                "authors": authors,
                                "citation_count": citation_count,
                                "full_text": ">\n" + full_text if full_text else ">",
                                "analysis": ">",
                                "verbatim_quote1": ">",
                                "verbatim_quote2": ">",
                                "verbatim_quote3": ">",
                                "relevance_score1": 0,
                                "relevance_score2": 0,
                                "limitations": ">",
                                "inline_citation": ">",
                                "full_citation": ">",
                            }
                        )

                hashed_filename = self.get_hashed_filename(query, query_id, response_id)
                output_path = self.save_yaml(parsed_results, hashed_filename)
                logger.info(f"Results saved successfully to: {output_path}")
                return output_path
        except Exception as e:
            logger.error(
                f"An error occurred while searching and parsing results for query: {query}. Error: {e}"
            )
            return ""

    def get_hashed_filename(self, query, query_id, response_id):
        hash_input = f"{query}_{query_id}_{response_id}"
        hashed_filename = sha256(hash_input.encode()).hexdigest()
        return f"{hashed_filename}.yaml"

    def save_yaml(self, data, filename):
        try:
            output_path = self.output_folder / filename
            # Create the output folder if it doesn't exist
            self.output_folder.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
            logger.info(f"YAML file saved successfully: {output_path}")
            return output_path.absolute()
        except Exception as e:
            logger.error(
                f"An error occurred while saving YAML file: {filename}. Error: {e}"
            )
            return ""
