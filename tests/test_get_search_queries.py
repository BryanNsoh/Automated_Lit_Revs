import pytest
from unittest.mock import AsyncMock, patch
from get_search_queries import QueryGenerator
from models import SearchQueries, SearchQuery

@pytest.mark.asyncio
async def test_generate_queries():
    generator = QueryGenerator()
    with patch('get_search_queries.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = [SearchQueries(queries=[
            SearchQuery(search_query="climate change AND water resources", query_rationale="Testing rationale 1"),
            SearchQuery(search_query="water scarcity AND hydrologist", query_rationale="Testing rationale 2"),
        ])]
        queries = await generator.generate_queries("impact of climate change on water resources", 2)
        assert len(queries.queries) == 2
        assert queries.queries[0].search_query == "climate change AND water resources"
