import asyncio
from typing import List

from llm_api_handler import LLMAPIHandler
from logger_config import get_logger
from models import SearchQueries

logger = get_logger(__name__)

CORE_SEARCH_GUIDE = """
### CORE API Search Guide: Formulating Queries

This guide provides a structured approach to creating effective search queries using the CORE API.

- Use field-specific searches (e.g., title, author, subject)
- Employ Boolean operators (AND, OR, NOT)
- Use parentheses () for grouping
- Utilize range queries (>, <, >=, <=)
- Check for existence with _exists_

Avoid inconsistent field names and improper boolean logic.

Example queries:
1. "climate change AND water resources"
2. "water scarcity AND (hydrologist OR water expert)"
3. "sea level rise AND coastal erosion"
4. "water conservation AND climate change mitigation AND environmental studies"
5. "glacier melting AND cryosphere"
"""

GENERATE_QUERIES_PROMPT = """
Review the user's main query: '{user_query}'. Create {num_queries} distinct sub-queries that address different aspects of the main query. For each sub-query, provide a rationale explaining its importance.

Format your response as a JSON object with the following structure:
{{
  "queries": [
    {{
      "search_query": "Your search query here",
      "query_rationale": "Your rationale for this query here"
    }},
    {{
      "search_query": "Your next search query here",
      "query_rationale": "Your rationale for this query here"
    }}
    // ... up to {num_queries} queries
  ]
}}

Generate {num_queries} sub-queries, each directly contributing to answering the main query.

Search Guidance:
{search_guidance}
"""

class QueryGenerator:
    def __init__(self):
        self.llm_api_handler = LLMAPIHandler()

    async def generate_queries(self, user_query: str, num_queries: int = 5) -> SearchQueries:
        prompt = GENERATE_QUERIES_PROMPT.format(
            user_query=user_query,
            num_queries=num_queries,
            search_guidance=CORE_SEARCH_GUIDE,
        )
        
        try:
            responses = await self.llm_api_handler.async_process(
                prompts=[prompt],
                model="gpt-4o-mini",
                response_format=SearchQueries
            )

            if responses and isinstance(responses[0], SearchQueries):
                return responses[0]
            else:
                logger.error(f"Unexpected response from LLMAPIHandler: {responses}")
                return SearchQueries(queries=[])
        except Exception as e:
            logger.error(f"Error generating queries: {str(e)}")
            return SearchQueries(queries=[])

async def main():
    processor = QueryGenerator()
    user_query = "Impact of climate change on global water resources"
    queries = await processor.generate_queries(user_query)
    print(queries.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
