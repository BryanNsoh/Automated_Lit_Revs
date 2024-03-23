"""
scopus_search.py

This module provides a ScopusSearch class for performing asynchronous searches on the Scopus API.
"""

import aiohttp
import asyncio
import time
from collections import deque


class ScopusSearch:
    """
    A class for performing asynchronous searches on the Scopus API.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.elsevier.com/content/search/scopus"
        self.request_times = deque(maxlen=6)

    async def search(self, query, count=25, view="COMPLETE", response_format="json"):
        """
        Performs an asynchronous search on the Scopus API.

        Parameters:
        - query (str): The search query.
        - count (int): The number of results to return (default: 25).
        - view (str): The view of the results (default: "COMPLETE").
        - response_format (str): The format of the response (default: "json").

        Returns:
        - dict: The JSON response containing the search results.
        """
        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": (
                "application/json"
                if response_format == "json"
                else "application/atom+xml"
            ),
        }

        params = {"query": query.replace("\\", ""), "count": count, "view": view}

        # Ensure compliance with the rate limit
        while True:
            current_time = time.time()
            if not self.request_times or current_time - self.request_times[0] >= 1:
                self.request_times.append(current_time)
                break
            else:
                await asyncio.sleep(0.1)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.base_url, headers=headers, params=params
            ) as response:
                if response_format == "json":
                    return await response.json()
                else:
                    return await response.text()

    async def search_and_parse(self, query, count=25, view="COMPLETE"):
        """
        Performs an asynchronous search on the Scopus API and parses the JSON response.

        Parameters:
        - query (str): The search query.
        - count (int): The number of results to return (default: 25).
        - view (str): The view of the results (default: "COMPLETE").

        Returns:
        - list: A list of dictionaries containing the parsed search results.
        """
        results = await self.search(query, count, view, response_format="json")

        if (
            results is None
            or "search-results" not in results
            or "entry" not in results["search-results"]
        ):
            return []
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

                if title is not None:
                    parsed_results.append(
                        {
                            "title": title,
                            "doi": doi,
                            "description": description,
                            "journal": journal,
                            "authors": authors,
                            "citation_count": citation_count,
                        }
                    )

            return parsed_results


# import asyncio
# from doi_scraper import DOIScraper

# async def main():
#     scraper = DOIScraper()
#     doi_link = "https://doi.org/example"
#     content = await scraper.get_doi_content(doi_link)
#     print(content)

# asyncio.run(main())
