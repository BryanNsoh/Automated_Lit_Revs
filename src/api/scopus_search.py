"""
Scopus Search Program

This program performs searches on the Scopus API based on the provided JSON queries.
It retrieves relevant data for the first entry with successfully scraped full text,
including title, DOI, description, journal, authors, citation count, and full text.
The results are returned in the updated JSON format.

Usage:
    scopus_search = ScopusSearch(doi_scraper)
    updated_json = scopus_search.search_and_parse_json(input_json)

Parameters:
    - doi_scraper: A scraper object capable of retrieving full text content given a DOI.
    - input_json: A JSON object containing the search queries in the specified format.

Returns:
    - updated_json: The updated JSON object with the search results and additional data.
"""

import aiohttp
import asyncio
import json
import time
from collections import deque
from src.utils.misc_utils import prepare_text_for_json, get_api_keys
from src.utils.web_scraper import WebScraper

from src.utils.logger_config import get_logger

logger = get_logger(__name__)


class ScopusSearch:
    def __init__(self, doi_scraper, session, max_retries=4):
        self.api_keys = get_api_keys()
        self.base_url = "http://api.elsevier.com/content/search/scopus"
        self.request_times = deque(maxlen=6)
        self.scraper = doi_scraper
        self.session = session
        self.max_retries = max_retries

    async def search(self, query, count=25, view="COMPLETE", response_format="json"):
        headers = {
            "X-ELS-APIKey": self.api_keys["SCOPUS_API_KEY"],
            "Accept": (
                "application/json"
                if response_format == "json"
                else "application/atom+xml"
            ),
        }

        params = {
            "query": query["search_query"].replace("\\", ""),
            "count": count,
            "view": view,
        }

        retry_count = 0
        while retry_count < self.max_retries:
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

                async with self.session.get(
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
                    f"Error occurred while making Scopus API request: {e}. Retrying in {wait_time} seconds... (Attempt {retry_count}/{self.max_retries})"
                )
                await asyncio.sleep(wait_time)  # Exponential backoff

        logger.error(
            f"Max retries ({self.max_retries}) exceeded. Unable to fetch data from the Scopus API for query: {query}"
        )
        return None

    async def search_and_parse(self, query, query_id, count=25, view="COMPLETE"):
        try:
            results = await self.search(query, count, view, response_format="json")

            if (
                results is None
                or "search-results" not in results
                or "entry" not in results["search-results"]
            ):
                logger.warning(f"No results found for query: {query}")
                return {}
            else:
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
                            continue

                    parsed_result = {
                        "search_query": query["search_query"],
                        "query_rationale": query["query_rationale"],
                        "title": title,
                        "DOI": doi,
                        "description": description,
                        "journal": journal,
                        "authors": authors,
                        "citation_count": citation_count,
                        "full_text": full_text or "",
                    }

                    return parsed_result

                logger.warning(f"No full text successfully scraped for query: {query}")
                return {}
        except Exception as e:
            logger.error(
                f"An error occurred while searching and parsing results for query: {query}. Error: {e}"
            )
            return {}

    async def search_and_parse_json(self, input_json):
        try:
            updated_json = {}
            for query_id, query in input_json.items():
                parsed_result = await self.search_and_parse(query, query_id)
                updated_json[query_id] = parsed_result
            return json.dumps(updated_json, ensure_ascii=False)
        except Exception as e:
            logger.error(
                f"An error occurred while processing the input JSON. Error: {e}"
            )
            return json.dumps({})


async def main():
    async with aiohttp.ClientSession() as session:
        doi_scraper = WebScraper(session)
        # Create an instance of the ScopusSearch class
        scopus_search = ScopusSearch(doi_scraper, session)

        # Example usage
        input_json = {
            "query_1": {
                "search_query": "TITLE-ABS-KEY(heart disease AND chickens AND pathology)",
                "query_rationale": "This query is essential to understand the pathology of heart disease in chickens, providing a foundation for further investigation.",
            },
            "query_2": {
                "search_query": "TITLE-ABS-KEY(heart disease AND chickens AND epidemiology)",
                "query_rationale": "This query is necessary to identify the prevalence and distribution of heart disease in chicken populations, informing strategies for disease control and prevention.",
            },
            "query_3": {
                "search_query": "TITLE-ABS-KEY(heart disease AND chickens AND nutrition)",
                "query_rationale": "This query is important to explore the relationship between nutrition and heart disease in chickens, potentially identifying dietary factors that contribute to the development of the disease.",
            },
            "query_4": {
                "search_query": "TITLE-ABS-KEY(heart disease AND chickens AND genetics)",
                "query_rationale": "This query is crucial to investigate the genetic factors that predispose chickens to heart disease, enabling the development of breeding programs that reduce the incidence of the disease.",
            },
            "query_5": {
                "search_query": "TITLE-ABS-KEY(heart disease AND chickens AND diagnosis)",
                "query_rationale": "This query is essential to identify effective diagnostic methods for heart disease in chickens, ensuring accurate and timely detection of the disease.",
            },
        }

        # Call the search_and_parse_json method
        updated_json = await scopus_search.search_and_parse_json(input_json)
        print(updated_json)


if __name__ == "__main__":
    asyncio.run(main())
