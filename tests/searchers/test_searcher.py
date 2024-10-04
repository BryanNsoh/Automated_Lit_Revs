import pytest
from searchers.searcher import Searcher
from models import SearchQueries, SearchResults

class MockSearcher(Searcher):
    async def search_and_parse_queries(self, search_queries: SearchQueries) -> SearchResults:
        return SearchResults(results=[])

@pytest.mark.asyncio
async def test_searcher_interface():
    searcher = MockSearcher()
    search_queries = SearchQueries(queries=[])
    results = await searcher.search_and_parse_queries(search_queries)
    assert isinstance(results, SearchResults)
