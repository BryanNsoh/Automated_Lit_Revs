import aiohttp
import asyncio
from typing import Dict, List
from misc_utils import get_api_keys
from models import SearchQueries, SearchResult, SearchResults, SearchQuery
from logger_config import get_logger
import os
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

class CORESearch:
    def __init__(self, max_results: int):
        self.base_url = "https://api.core.ac.uk/v3"
        self.max_results = max_results
        self.core_api_key = os.getenv("CORE_API_KEY")

    async def search(self, search_query: str) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.core_api_key}",
            "Accept": "application/json",
        }

        params = {
            "q": search_query,
            "limit": self.max_results,
            "fulltext": "true",  # Request full text in the response
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
                    DOI=entry.get("doi") or "",
                    authors=[author["name"] for author in entry.get("authors", [])],
                    citation_count=entry.get("citationCount", 0),
                    journal=entry.get("publisher", ""),
                    pdf_link=entry.get("downloadUrl", ""),
                    publication_year=entry.get("publicationYear"),
                    title=entry.get("title", ""),
                    full_text=entry.get("fullText", ""),  # New field for full text
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
            results = SearchResults(results=[])
            for query in search_queries.queries:
                result = await self.search_and_parse(query.search_query, query)
                results.results.append(result)
            return results
        except Exception as e:
            logger.error(
                f"An error occurred while processing the search queries. Error: {e}"
            )
            return SearchResults(results=[])

async def main():
    max_results = 1
    core_search = CORESearch(max_results)

    # Example usage
    search_queries = SearchQueries(queries=[
        SearchQuery(
            search_query="climate change",
            query_rationale="Understanding how climate change affects the availability of freshwater is crucial for water management and planning strategies."
        ),
        SearchQuery(
            search_query="effects of climate change on groundwater resources",
            query_rationale="Groundwater is a key resource for drinking water and irrigation; assessing its vulnerability to climate changes is essential for sustainable use."
        ),
        # ... (you can add more queries here)
    ])

    results = await core_search.search_and_parse_queries(search_queries)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
