import asyncio
from typing import Dict, List
from pydantic import BaseModel, Field

from llm_api_handler import LLMAPIHandler
from models import Paper
from logger_config import get_logger

logger = get_logger(__name__)

# Add the core_search_guide here (unchanged)
CORE_SEARCH_GUIDE = """
### CORE API Search Guide: Formulating Queries in JSON Format

This guide provides a structured approach to creating effective search queries using the CORE API. The guide emphasizes the JSON format to ensure clarity and precision in your search queries.

#### Syntax and Operators

**Valid Syntax for CORE API Queries:**
- **Field-specific searches**: Direct your query to search within specific fields like `title`, `author`, or `subject`.
- **Boolean Operators**: Use `AND`, `OR`, and `NOT` to combine or exclude terms.
- **Grouping**: Use parentheses `()` to structure the query and define the order of operations.
- **Range Queries**: Specify ranges for dates or numerical values with `>`, `<`, `>=`, `<=`.
- **Existence Check**: Use `_exists_` to filter results based on the presence of data in specified fields.

**Invalid Syntax:**
- **Inconsistencies in field names**: Ensure field names are correctly spelled and appropriate for the data type.
- **Improper boolean logic**: Avoid illogical combinations that nullify the search criteria (e.g., `AND NOT` used incorrectly).

#### Ideal Query Structure

Your search queries should:
1. **Use Field-Specific Filters**: Focus your search on the most relevant attributes.
2. **Combine Keywords Effectively**: Use logical operators to refine and broaden your searches.
3. **Employ Grouping and Range Queries** where complex relationships or specific time frames are needed.

#### Example Advanced Searches in JSON Format

Here are examples of structured queries formatted in JSON, demonstrating different ways to effectively combine search criteria using the CORE API:

{
    "query_1": {
        "search_query": "climate change, water resources",
        "query_rationale": "This query is essential to understand the overall impact of climate change on global water resources, providing a broad understanding of the topic.",
    },
    "query_2": {
        "search_query": "water scarcity, (hydrologist OR water expert)",
        "query_rationale": "This query is necessary to identify areas with high water scarcity and how climate change affects the global distribution of water resources.",
    },
    "query_3": {
        "search_query": "sea level rise, coastal erosion",
        "query_rationale": "This query is crucial to understand the impact of climate change on coastal regions and the resulting effects on global water resources.",
    },
    "query_4": {
        "search_query": "water conservation, climate change mitigation, environmental studies",
        "query_rationale": "This query is important to identify strategies for water conservation and their role in mitigating the effects of climate change on global water resources.",
    },
    "query_5": {
        "search_query": "glacier melting, cryosphere",
        "query_rationale": "This query is necessary to understand the impact of climate change on glaciers and the resulting effects on global water resources.",
    },
}
"""

# Add the full prompt here (unchanged)
GENERATE_QUERIES_PROMPT = """
<documents>
<document index="1">
<source>search_query_prompt.txt</source>
<document_content>
<instructions>
Review the user's main query: '{user_query}'. Break down this query into distinct sub-queries that address different aspects necessary to fully answer the main query. 
For each sub-query, provide a rationale explaining why it is essential. Format these sub-queries according to the directions in <search_guidance>. structure your response as a json with detailed search queries, each accompanied by its rationale. 
The output should adhere to this format:
{{
  "query_1": {{
    "search_query": "unique query following the provided search guidance",
    "query_rationale": "This query is essential to understand the overall impact of climate change on global water resources, providing a broad understanding of the topic."
  }},
  "query_2": {{
    "search_query": "unique query following the provided search guidance",
    "query_rationale": "This query is necessary to identify areas with high water scarcity and how climate change affects the global distribution of water resources."
  }},
  ...
}}
**Note: Only generate as many sub-queries and rationales as necessary to thoroughly address the main query, up to a maximum of 10. Each sub-query must directly contribute to unraveling the main query's aspects.
</instructions>
<search_guidance>
{search_guidance}
</search_guidance>
</resources>
</document_content>
</document>
</documents>
"""

class SearchQuery(BaseModel):
    search_query: str
    query_rationale: str

class SearchQueries(BaseModel):
    queries: Dict[str, SearchQuery] = Field(..., description="A dictionary of search queries")

class QueryGenerator:
    def __init__(self):
        self.llm_api_handler = LLMAPIHandler()

    async def generate_queries(self, user_query: str) -> SearchQueries:
        prompt = GENERATE_QUERIES_PROMPT.format(
            user_query=user_query,
            search_guidance=CORE_SEARCH_GUIDE,
        )

        try:
            response = await self.llm_api_handler.process(
                prompts=[prompt],
                model="gpt-4o-mini",
                mode="async",
                response_format=SearchQueries
            )

            if response and isinstance(response[0], SearchQueries):
                return response[0]
            else:
                logger.error(f"Unexpected response from LLMAPIHandler: {response}")
                return SearchQueries(queries={})  # Return an empty SearchQueries object
        except Exception as e:
            logger.error(f"Error generating queries: {str(e)}")
            return SearchQueries(queries={})  # Return an empty SearchQueries object

async def main():
    processor = QueryGenerator()
    user_query = "Impact of climate change on global water resources"
    queries = await processor.generate_queries(user_query)
    print(queries.json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
