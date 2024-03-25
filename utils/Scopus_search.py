import aiohttp
import asyncio
import json
import time

from collections import deque
from misc_utils import prepare_text_for_json


class ScopusSearch:
    """
    A class for performing asynchronous searches on the Scopus API.
    """

    def __init__(self, key_path, doi_scraper):
        self.load_api_keys(key_path)
        self.base_url = "http://api.elsevier.com/content/search/scopus"
        self.request_times = deque(maxlen=6)
        self.scraper = doi_scraper

    def load_api_keys(self, key_path):
        """
        Load the API keys from the specified JSON file.
        """
        with open(key_path, "r") as file:
            api_keys = json.load(file)
        self.api_key = api_keys["SCOPUS_API_KEY"]

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

                full_text = None
                if doi:
                    print(f"Scraping full text for DOI: {doi}")
                    full_text = await self.scraper.get_doi_content(doi)
                    full_text = await prepare_text_for_json(full_text)
                print("At least 1 search scraped")
                if title is not None:
                    parsed_results.append(
                        {
                            "title": title,
                            "doi": doi,
                            "description": description,
                            "journal": journal,
                            "authors": authors,
                            "citation_count": citation_count,
                            "full_text": full_text,
                            "analysis": "",
                            "verbatim_quote1": "",
                            "verbatim_quote2": "",
                            "verbatim_quote3": "",
                            "relevance_score1": 0,
                            "relevance_score2": 0,
                            "limitations": "",
                            "inline_citation": "",
                            "full_citation": "",
                        }
                    )

            return json.dumps(parsed_results, indent=2)


# # Sample function call
# async def main():
#     from utils.web_scraper import WebScraper

#     scraper = WebScraper()
#     search = ScopusSearch(
#         key_path=r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json",
#         doi_scraper=scraper,
#     )
#     query = "artificial intelligence"
#     print("Searching for:", query)
#     results = await search.search_and_parse(query)
#     print("Results:", results)
#     # save the results to a file
#     with open("scopus_results.json", "w") as f:
#         f.write(results)
#     print(results)


# asyncio.run(main())
