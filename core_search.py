import aiohttp
import asyncio
from typing import Dict, List
from misc_utils import get_api_keys
from models import SearchQueries, SearchResult, SearchResults, SearchQuery
from logger_config import get_logger
import os
from dotenv import load_dotenv
from time import time

load_dotenv()

logger = get_logger(__name__)

class RateLimiter:
    """
    A simple asynchronous rate limiter that restricts the number of actions
    within a given time period.
    """
    def __init__(self, max_requests: int, period: int):
        self.max_requests = max_requests
        self.period = period
        self.requests = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            current = time()
            # Remove timestamps older than the period
            self.requests = [req for req in self.requests if req > current - self.period]
            if len(self.requests) >= self.max_requests:
                # Calculate the time to wait until the next request is allowed
                earliest = self.requests[0]
                wait_time = self.period - (current - earliest)
                logger.info(f"Rate limit reached. Waiting for {wait_time:.2f} seconds.")
                await asyncio.sleep(wait_time)
            self.requests.append(time())

class CORESearch:
    def __init__(self, max_results: int, max_requests_per_minute: int = 5):
        self.base_url = "https://api.core.ac.uk/v3"
        self.max_results = max_results
        self.api_keys = self.load_api_keys()
        self.current_key_index = 0
        self.rate_limiter = RateLimiter(max_requests_per_minute, 60)
        self.session = aiohttp.ClientSession()
    
    def load_api_keys(self) -> List[str]:
        """
        Load API keys from environment variables. Supports multiple keys for rotation.
        """
        keys = []
        # Attempt to load CORE_API_KEY1 to CORE_API_KEY4
        for key_num in range(1, 5):
            key = os.getenv(f"CORE_API_KEY{key_num}")
            if key:
                keys.append(key)
        # Fallback to CORE_API_KEY if others are not set
        if not keys:
            key = os.getenv("CORE_API_KEY")
            if key:
                keys.append(key)
        if not keys:
            logger.error("No API keys found in environment variables.")
            raise ValueError("No API keys found. Please set CORE_API_KEY or CORE_API_KEY1 to CORE_API_KEY4.")
        logger.info(f"Loaded {len(keys)} API key(s).")
        return keys

    async def get_current_api_key(self) -> str:
        """
        Retrieve the current API key.
        """
        return self.api_keys[self.current_key_index]

    async def rotate_api_key(self):
        """
        Rotate to the next API key in the list.
        """
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"Rotated to API key index: {self.current_key_index + 1}/{len(self.api_keys)}")
        await asyncio.sleep(1)  # Small delay to prevent immediate retries

    async def search(self, search_query: str) -> Dict:
        """
        Perform a search query against the CORE API with rate limiting and key rotation.
        """
        await self.rate_limiter.acquire()  # Enforce rate limit before making a request

        headers = {
            "Authorization": f"Bearer {await self.get_current_api_key()}",
            "Accept": "application/json",
        }

        params = {
            "q": search_query,
            "limit": self.max_results,
            "fulltext": "true",  # Request full text in the response
        }

        try:
            async with self.session.post(
                f"{self.base_url}/search/works", headers=headers, json=params
            ) as response:
                # Extract rate limit headers
                remaining = response.headers.get("X-RateLimitRemaining", "Unknown")
                reset = response.headers.get("X-RateLimit-Reset", "Unknown")
                logger.info(f"Rate Limit Remaining: {remaining}, Reset Time: {reset}")

                if response.status == 200:
                    logger.info("CORE API request successful.")
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Received 429 Too Many Requests. Rotating API key and retrying.")
                    await self.rotate_api_key()
                    return await self.search(search_query)  # Retry with next key
                else:
                    logger.warning(
                        f"CORE API request failed with status code: {response.status}"
                    )
                    return {}
        except aiohttp.ClientError as e:
            logger.error(f"HTTP Client error: {e}")
            return {}

    async def search_and_parse(self, query_id: str, search_query: SearchQuery) -> SearchResult:
        """
        Perform a search and parse the result into a SearchResult object.
        """
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
                    full_text=entry.get("fullText", ""),
                    search_query=search_query.search_query,
                    query_rationale=search_query.query_rationale
                )

            return SearchResult(query_rationale=search_query.query_rationale)
        except Exception as e:
            logger.error(
                f"An error occurred while searching and parsing results for query: {search_query.search_query}. Error: {e}"
            )
            return SearchResult(query_rationale=search_query.query_rationale)

    async def search_and_parse_queries(self, search_queries: SearchQueries) -> SearchResults:
        """
        Process multiple search queries asynchronously.
        """
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

    async def close(self):
        """
        Close the aiohttp session gracefully.
        """
        await self.session.close()

async def main():
    max_results = 1
    # Set a more conservative rate limit, e.g., 5 requests per minute
    core_search = CORESearch(max_results, max_requests_per_minute=5)

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

    await core_search.close()

if __name__ == "__main__":
    asyncio.run(main())
