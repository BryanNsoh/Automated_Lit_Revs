# searchers/core_search.py
import aiohttp
import asyncio
from typing import Dict, List
from misc_utils import get_api_keys
from models import SearchQueries, SearchResult, SearchResults, SearchQuery
from logger_config import get_logger
import os
from dotenv import load_dotenv
from time import time
from .searcher import Searcher
import random  # Added for random key selection

load_dotenv(override=True)

logger = get_logger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int, period: int):
        self.max_requests = max_requests
        self.period = period
        self.requests = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            current = time()
            self.requests = [req for req in self.requests if req > current - self.period]
            if len(self.requests) >= self.max_requests:
                earliest = self.requests[0]
                wait_time = self.period - (current - earliest)
                logger.info(f"Rate limit reached. Waiting for {wait_time:.2f} seconds.")
                await asyncio.sleep(wait_time)
            self.requests.append(time())

class CORESearch(Searcher):
    def __init__(self, max_results: int = 10, max_requests_per_minute: int = 5):
        self.base_url = "https://api.core.ac.uk/v3"
        self.max_results = max_results
        self.api_keys = self.load_api_keys()
        # Removed current_key_index as rotation is now random
        self.rate_limiter = RateLimiter(max_requests_per_minute, 60)
        self.session = aiohttp.ClientSession()
    
    def load_api_keys(self) -> List[str]:
        keys = []
        for key_num in range(1, 5):
            key = os.getenv(f"CORE_API_KEY{key_num}")
            if key:
                keys.append(key)
        if not keys:
            key = os.getenv("CORE_API_KEY")
            if key:
                keys.append(key)
        if not keys:
            logger.error("No API keys found in environment variables.")
            raise ValueError("No API keys found. Please set CORE_API_KEY or CORE_API_KEY1 to CORE_API_KEY4.")
        logger.info(f"Loaded {len(keys)} API key(s).")
        return keys

    async def get_random_api_key(self) -> str:
        key = random.choice(self.api_keys)
        logger.debug(f"Selected random CORE API key: {key[:4]}****")  # Logging partially for security
        return key

    async def search(self, search_query: str) -> Dict:
        await self.rate_limiter.acquire()

        headers = {
            "Authorization": f"Bearer {await self.get_random_api_key()}",
            "Accept": "application/json",
        }

        params = {
            "q": search_query,
            "limit": self.max_results,
            "fulltext": "true",
        }

        try:
            async with self.session.post(
                f"{self.base_url}/search/works", headers=headers, json=params
            ) as response:
                remaining = response.headers.get("X-RateLimitRemaining", "Unknown")
                reset = response.headers.get("X-RateLimitReset", "Unknown")
                logger.info(f"Rate Limit Remaining: {remaining}, Reset Time: {reset}")

                if response.status == 200:
                    logger.info("CORE API request successful.")
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Received 429 Too Many Requests. Attempting with a different API key.")
                    # Recursive call with a different API key
                    return await self.search(search_query)
                else:
                    logger.warning(
                        f"CORE API request failed with status code: {response.status}"
                    )
                    return {}
        except aiohttp.ClientError as e:
            logger.error(f"HTTP Client error: {e}")
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
                    publication_year=int(entry.get("publicationYear")) if entry.get("publicationYear") else None,
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
        try:
            results = SearchResults(results=[])
            for query in search_queries.queries:
                result = await self.search_and_parse(query.search_query, query)
                results.results.append(result)
                if len(results.results) >= self.max_results:
                    break
            return results
        except Exception as e:
            logger.error(
                f"An error occurred while processing the search queries. Error: {e}"
            )
            return SearchResults(results=[])

    async def close(self):
        await self.session.close()

# Ensure the CORESearch class is exported
__all__ = ['CORESearch']
