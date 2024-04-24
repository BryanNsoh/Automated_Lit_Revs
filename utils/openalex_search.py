import aiohttp
import asyncio
import json
import fitz
import urllib.parse
import yaml
from web_scraper import WebScraper
from pathlib import Path

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
    def __init__(self, email, web_scraper, session):
        self.base_url = "https://api.openalex.org"
        self.email = email
        self.web_scraper = web_scraper
        self.semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
        self.session = session

    async def search_papers(self, query, query_id, max_results=30):
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
                    async with self.session.get(search_url) as response:
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
                                    for work in data["results"]:
                                        paper = {
                                            "DOI": (
                                                work["doi"] if "doi" in work else ""
                                            ),
                                            "authors": (
                                                [
                                                    author["author"]["display_name"]
                                                    for author in work["authorships"]
                                                ]
                                                if "authorships" in work
                                                else []
                                            ),
                                            "citation_count": (
                                                work["cited_by_count"]
                                                if "cited_by_count" in work
                                                else 0
                                            ),
                                            "full_text": ">",
                                            "journal": (
                                                work["primary_location"]["source"][
                                                    "display_name"
                                                ]
                                                if "primary_location" in work
                                                and isinstance(
                                                    work["primary_location"], dict
                                                )
                                                and "source" in work["primary_location"]
                                                and isinstance(
                                                    work["primary_location"]["source"],
                                                    dict,
                                                )
                                                and "display_name"
                                                in work["primary_location"]["source"]
                                                else ""
                                            ),
                                            "pdf_link": (
                                                work["primary_location"]["pdf_url"]
                                                if "primary_location" in work
                                                and isinstance(
                                                    work["primary_location"], dict
                                                )
                                                and "pdf_url"
                                                in work["primary_location"]
                                                else ""
                                            ),
                                            "publication_year": (
                                                work["publication_year"]
                                                if "publication_year" in work
                                                else ""
                                            ),
                                            "title": (
                                                work["title"] if "title" in work else ""
                                            ),
                                        }

                                        full_text = ""  # Initialize full_text with an empty string

                                        try:
                                            if paper["pdf_link"]:
                                                logger.info(
                                                    f"Extracting full text from PDF URL: {paper['pdf_link']}"
                                                )
                                                full_text = await self.extract_fulltext(
                                                    paper["pdf_link"]
                                                )
                                                if not full_text:
                                                    logger.info(
                                                        f"Extracting full text from URL: {paper['pdf_link']}"
                                                    )
                                                    full_text = await self.extract_fulltext_from_url(
                                                        paper["pdf_link"]
                                                    )

                                            if not full_text and paper["DOI"]:
                                                logger.info(
                                                    f"Extracting full text from DOI: {paper['DOI']}"
                                                )
                                                full_text = await self.extract_fulltext_from_doi(
                                                    paper["DOI"]
                                                )

                                            if full_text:
                                                logger.info(
                                                    "Full text extracted successfully."
                                                )
                                                paper["full_text"] = ">\n" + full_text
                                                return json.dumps(
                                                    {query_id: paper},
                                                    ensure_ascii=False,
                                                )
                                            else:
                                                logger.warning(
                                                    "Failed to extract full text."
                                                )
                                        except Exception as e:
                                            logger.error(
                                                f"Error occurred while extracting full text: {str(e)}"
                                            )

                                    logger.warning(
                                        f"No full text successfully scraped for query: {query}"
                                    )
                                    return json.dumps({query_id: {}})
                                else:
                                    logger.warning(
                                        f"Unexpected JSON structure from OpenAlex API: {data}"
                                    )
                                    return json.dumps({query_id: {}})
                            else:
                                logger.error(
                                    f"Unexpected content type from OpenAlex API: {response.content_type}"
                                )
                                logger.error(f"URL: {search_url}")
                                logger.error(await response.text())
                                return json.dumps({query_id: {}})
                        else:
                            logger.error(
                                f"Unexpected status code from OpenAlex API: {response.status}"
                            )
                            logger.error(f"URL: {search_url}")
                            logger.error(await response.text())
                            return json.dumps({query_id: {}})
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
                        return json.dumps({query_id: {}})
                except aiohttp.ClientError as error:
                    logger.exception(
                        f"Error occurred while making request to OpenAlex API: {str(error)}"
                    )
                    retries += 1
                    if retries < max_retries:
                        logger.warning(f"Retrying request in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Max retries exceeded for URL: {search_url}")
                        return json.dumps({query_id: {}})

        logger.error(f"Max retries exceeded for URL: {search_url}")
        return json.dumps({query_id: {}})

    async def extract_fulltext(self, pdf_url):
        try:
            async with self.session.get(pdf_url) as resp:
                pdf_bytes = await resp.read()
                try:
                    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                        fulltext = ""
                        for page in doc:
                            fulltext += page.get_text()
                        logger.info(f"Full text extracted from PDF: {pdf_url}")
                        return fulltext
                except fitz.FileDataError:
                    logger.error(f"Error: Cannot open PDF file from {pdf_url}")
                    return ""
        except aiohttp.ClientError as e:
            logger.error(f"Error occurred while retrieving PDF from {pdf_url}")
            logger.error(f"Error details: {str(e)}")
            return ""
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while extracting full text from {pdf_url}"
            )
            logger.error(f"Error details: {str(e)}")
            return ""

    async def extract_fulltext_from_url(self, pdf_url):
        try:
            logger.info(f"Extracting full text from URL: {pdf_url}")
            content = await self.web_scraper.get_url_content(pdf_url)
            logger.info(f"Full text extracted from URL: {pdf_url}")
            return content
        except Exception as e:
            logger.error(
                f"Error: Failed to scrape full text from PDF URL {pdf_url}. {str(e)}"
            )
            return ""

    async def extract_fulltext_from_doi(self, doi):
        try:
            logger.info(f"Extracting full text from DOI: {doi}")
            content = await self.web_scraper.get_url_content(doi)
            logger.info(f"Full text extracted from DOI: {doi}")
            return content
        except Exception as e:
            logger.error(f"Error: Failed to scrape full text from DOI {doi}. {str(e)}")
            return ""

    async def search_and_parse_json(self, input_json):
        try:
            updated_json = {}
            for query_id, query in input_json.items():
                parsed_result = await self.search_papers(query, query_id)
                updated_json.update(json.loads(parsed_result))
            return json.dumps(updated_json, ensure_ascii=False)
        except Exception as e:
            logger.error(
                f"An error occurred while processing the input JSON. Error: {e}"
            )
            return json.dumps({})


async def main():
    # Create an instance of the WebScraper class (assuming it exists)
    web_scraper = WebScraper()

    async with aiohttp.ClientSession() as session:
        # Create an instance of the OpenAlexPaperSearch class
        openalex_search = OpenAlexPaperSearch(
            email="your_email@example.com", web_scraper=web_scraper, session=session
        )

        # Example usage
        input_json = {
            "query_1": "heart disease chickens",
            "query_2": "cardiovascular disease poultry",
            "query_3": "heart failure broiler chickens",
            "query_4": "myocarditis chickens",
            "query_5": "pericarditis poultry",
        }

        # Call the search_and_parse_json method
        updated_json = await openalex_search.search_and_parse_json(input_json)
        print(updated_json)


if __name__ == "__main__":
    asyncio.run(main())
