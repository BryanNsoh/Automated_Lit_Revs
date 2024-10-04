import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from analyze_papers import PaperAnalyzer
from models import SearchResults, SearchResult, RankedPapers

@pytest.fixture
def mock_search_results():
    full_text = " " .join(["This is a test sentence."] * 50)  # 50 sentences to exceed 200 words
    return SearchResults(results=[
        SearchResult(
            DOI="10.1234/test.doi",
            authors=["Author One", "Author Two"],
            citation_count=10,
            journal="Journal of Testing",
            pdf_link="http://example.com/test.pdf",
            publication_year=2021,
            title="Test Paper Title",
            full_text=full_text,
            search_query="impact of climate change",
            query_rationale="Testing impact queries"
        )
    ])

@pytest.mark.asyncio
async def test_analyze_papers_ranking(mock_search_results):
    analyzer = PaperAnalyzer()
    with patch('analyze_papers.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm:
        # Mock the LLMAPIHandler responses
        mock_llm.return_value = [{
            "rankings": [
                {"paper_id": "paper_0", "rank": 1, "explanation": "Highly relevant"},
            ]
        }]
        ranked_papers = await analyzer.analyze_papers(mock_search_results, "impact of climate change")
        assert len(ranked_papers.papers) == 1
        assert ranked_papers.papers[0].relevance_score > 0

@pytest.mark.asyncio
async def test_analyze_paper_analysis(mock_search_results):
    analyzer = PaperAnalyzer()
    paper = mock_search_results.results[0]
    with patch('analyze_papers.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = [ {
            "analysis": "This paper is highly relevant.",
            "relevant_quotes": ["Significant impact on climate change."]
        }]
        analysis = await analyzer.analyze_paper("impact of climate change", paper)
        assert analysis.analysis == "This paper is highly relevant."
        assert len(analysis.relevant_quotes) == 1
