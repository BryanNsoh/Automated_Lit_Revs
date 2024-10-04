import pytest
from unittest.mock import AsyncMock, patch
from searchers.core_search import CORESearch
from models import SearchQueries, SearchQuery, SearchResults

@pytest.mark.asyncio
async def test_core_search_success():
    core_search = CORESearch(max_results=1)
    with patch.object(core_search, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {
            'results': [{
                'doi': '10.1234/core.doi',
                'title': 'Core Test Paper',
                'authors': [{'name': 'Core Author'}],
                'publicationYear': '2021',
                'fullText': 'Full text of the core paper.'
            }]
        }
        search_queries = SearchQueries(queries=[
            SearchQuery(search_query="data science", query_rationale="Test rationale")
        ])
        results = await core_search.search_and_parse_queries(search_queries)
        assert len(results.results) == 1
        assert results.results[0].title == 'Core Test Paper'
