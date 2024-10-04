import pytest
from unittest.mock import AsyncMock, patch
from searchers.arxiv_search import ArXivSearch
from models import SearchQueries, SearchQuery, SearchResults

@pytest.mark.asyncio
async def test_arxiv_search_success():
    arxiv_search = ArXivSearch(max_results=1)
    with patch.object(arxiv_search, 'search', new_callable=AsyncMock) as mock_search, \
         patch.object(arxiv_search, 'get_full_text', new_callable=AsyncMock) as mock_get_full_text:
        mock_search.return_value = [{
            'id': 'arxiv:1234.5678',
            'title': 'ArXiv Test Paper',
            'authors': ['ArXiv Author'],
            'published': '2021-01-01T00:00:00Z',
            'pdf_url': 'http://example.com/arxiv.pdf',
        }]
        mock_get_full_text.return_value = 'Full text of the arXiv paper.'
        search_queries = SearchQueries(queries=[
            SearchQuery(search_query="machine learning", query_rationale="Test rationale")
        ])
        results = await arxiv_search.search_and_parse_queries(search_queries)
        assert len(results.results) == 1
        assert results.results[0].title == 'ArXiv Test Paper'
