import aiohttp
import asyncio
from typing import Dict
from misc_utils import get_api_keys
from models import SearchQueries, SearchResult, SearchResults, SearchQuery
from logger_config import get_logger

logger = get_logger(__name__)

class CORESearch:
    def __init__(self, max_results: int):
        self.api_keys = get_api_keys()
        self.base_url = "https://api.core.ac.uk/v3"
        self.max_results = max_results
        self.core_api_key = self.api_keys["CORE_API_KEY"]

    async def search(self, search_query: str) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.core_api_key}",
            "Accept": "application/json",
        }

        params = {
            "q": search_query,
            "limit": self.max_results,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/search/works", headers=headers, json=params
            ) as response:
                if response.status == 200:
                    logger.info("CORE API request successful.")
                    return await response.json()
                else:
                    logger.warning(
                        f"CORE API request failed with status code: {response.status}"
                    )
                    return {}

    async def search_and_parse(self, query_id: str, search_query: SearchQuery) -> SearchResult:
        try:
            response = await self.search(search_query.search_query)

            if not response:
                logger.warning(f"Empty API response for query: {search_query.search_query}")
                return SearchResult(query_rationale=search_query.query_rationale)

            results = response.get("results", [])

            if results:
                entry = results[0]
                return SearchResult(
                    DOI=entry.get("doi", ""),
                    authors=[author["name"] for author in entry.get("authors", [])],
                    citation_count=entry.get("citationCount", 0),
                    journal=entry.get("publisher", ""),
                    pdf_link=entry.get("downloadUrl", ""),
                    publication_year=entry.get("publicationYear"),
                    title=entry.get("title", ""),
                    query_rationale=search_query.query_rationale
                )

            return SearchResult(query_rationale=search_query.query_rationale)
        except Exception as e:
            logger.error(
                f"An error occurred while searching and parsing results for query: {search_query.search_query}. Error: {e}"
            )
            return SearchResult(query_rationale=search_query.query_rationale)

    async def search_and_parse_queries(self, search_queries: SearchQueries) -> SearchResults:
        try:
            results = SearchResults()
            for query_id, query in search_queries.queries.items():
                result = await self.search_and_parse(query_id, query)
                results.results[query_id] = result
            return results
        except Exception as e:
            logger.error(
                f"An error occurred while processing the search queries. Error: {e}"
            )
            return SearchResults()

async def main():
    max_results = 1
    core_search = CORESearch(max_results)

    # Example usage
    search_queries = SearchQueries(queries={
        "query_1": SearchQuery(
            search_query="climate change, water resources",
            query_rationale="This query is essential to understand the overall impact of climate change on global water resources."
        ),
        "query_2": SearchQuery(
            search_query="water scarcity, (hydrologist OR water expert)",
            query_rationale="This query is necessary to identify areas with high water scarcity."
        )
    })

    results = await core_search.search_and_parse_queries(search_queries)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
