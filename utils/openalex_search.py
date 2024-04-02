import aiohttp
import asyncio
import json
import urllib.parse
import yaml
from hashlib import sha256

import logging

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
file_handler = logging.FileHandler("alex.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class OpenAlexPaperSearch:
    def __init__(self, email, web_scraper, output_folder):
        self.base_url = "https://api.openalex.org"
        self.email = email
        self.web_scraper = web_scraper
        self.output_folder = output_folder
        self.semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

    async def search_papers(
        self, query, query_id, response_id, content, max_results=30
    ):
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=600)
        ) as session:
            if query.startswith("https://api.openalex.org/works?"):
                search_url = f"{query}&mailto={self.email}"
            else:
                encoded_query = urllib.parse.quote(query)
                search_url = f"{self.base_url}/works?search={encoded_query}&per_page={max_results}&mailto={self.email}"

            retries = 0
            max_retries = 3
            retry_delay = 1

            while retries < max_retries:
                async with self.semaphore:
                    try:
                        await asyncio.sleep(
                            0.2
                        )  # Wait for 0.2 seconds between requests to comply with rate limits
                        async with session.get(search_url) as response:
                            if response.status == 429:
                                logger.warning(
                                    f"Rate limit exceeded. Retrying in {retry_delay} seconds..."
                                )
                                await asyncio.sleep(retry_delay)
                                retries += 1
                                retry_delay *= 2  # Exponential backoff
                            elif response.status == 200:
                                if response.content_type == "application/json":
                                    data = await response.json()

                                    if "results" in data:
                                        paper_data = []
                                        for work in data["results"][:25]:
                                            paper = {
                                                "DOI": (
                                                    work["doi"] if "doi" in work else ""
                                                ),
                                                "authors": (
                                                    [
                                                        author["author"]["display_name"]
                                                        for author in work[
                                                            "authorships"
                                                        ]
                                                    ]
                                                    if "authorships" in work
                                                    else []
                                                ),
                                                "citation_count": (
                                                    work["cited_by_count"]
                                                    if "cited_by_count" in work
                                                    else 0
                                                ),
                                                "full_citation": ">",
                                                "full_text": ">",
                                                "analysis": ">",
                                                "verbatim_quote1": ">",
                                                "verbatim_quote2": ">",
                                                "verbatim_quote3": ">",
                                                "relevance_score1": 0,
                                                "relevance_score2": 0,
                                                "limitations": ">",
                                                "inline_citation": ">",
                                                "journal": (
                                                    work["primary_location"]["source"][
                                                        "display_name"
                                                    ]
                                                    if "primary_location" in work
                                                    and isinstance(
                                                        work["primary_location"], dict
                                                    )
                                                    and "source"
                                                    in work["primary_location"]
                                                    and isinstance(
                                                        work["primary_location"][
                                                            "source"
                                                        ],
                                                        dict,
                                                    )
                                                    and "display_name"
                                                    in work["primary_location"][
                                                        "source"
                                                    ]
                                                    else ""
                                                ),
                                                "publication_year": (
                                                    work["publication_year"]
                                                    if "publication_year" in work
                                                    else ""
                                                ),
                                                "title": (
                                                    work["title"]
                                                    if "title" in work
                                                    else ""
                                                ),
                                            }

                                            full_text = ""  # Initialize full_text with an empty string

                                            try:
                                                if paper["DOI"]:
                                                    logger.info(
                                                        f"Extracting full text from DOI: {paper['DOI']}"
                                                    )
                                                    full_text = content

                                                if full_text:
                                                    logger.info(
                                                        "Full text extracted successfully."
                                                    )
                                                    paper["full_text"] = (
                                                        ">\n" + full_text
                                                    )
                                                else:
                                                    logger.warning(
                                                        "Failed to extract full text."
                                                    )
                                            except Exception as e:
                                                logger.error(
                                                    f"Error occurred whileextracting full text: {str(e)}"
                                                )

                                            paper_data.append(paper)

                                        hashed_filename = self.get_hashed_filename(
                                            query, query_id, response_id
                                        )
                                        output_path = self.save_yaml(
                                            paper_data, hashed_filename
                                        )
                                        logger.info(
                                            f"Saved paper data to: {output_path}"
                                        )
                                        return output_path
                                    else:
                                        logger.warning(
                                            f"Unexpected JSON structure from OpenAlex API: {data}"
                                        )
                                        return ""
                                else:
                                    logger.error(
                                        f"Unexpected content type from OpenAlex API: {response.content_type}"
                                    )
                                    logger.error(f"URL: {search_url}")
                                    logger.error(await response.text())
                                    return ""
                            else:
                                logger.error(
                                    f"Unexpected status code from OpenAlex API: {response.status}"
                                )
                                logger.error(f"URL: {search_url}")
                                logger.error(await response.text())
                                return ""
                    except asyncio.TimeoutError:
                        logger.warning(
                            f"Request timed out. Retrying in {retry_delay} seconds..."
                        )
                        retries += 1
                        if retries < max_retries:
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(f"Max retries exceeded for URL: {search_url}")
                            return ""
                    except aiohttp.ClientError as error:
                        logger.exception(
                            f"Error occurred while making request to OpenAlex API: {str(error)}"
                        )
                        retries += 1
                        if retries < max_retries:
                            logger.warning(
                                f"Retrying request in {retry_delay} seconds..."
                            )
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(f"Max retries exceeded for URL: {search_url}")
                            return ""

            logger.error(f"Max retries exceeded for URL: {search_url}")
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
