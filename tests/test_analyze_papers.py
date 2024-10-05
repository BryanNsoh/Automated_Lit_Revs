import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from analyze_papers import PaperAnalyzer
from models import SearchResults, SearchResult, RankedPapers, PaperAnalysis, RankingResponse, PaperRanking

@pytest.fixture
def mock_search_results():
    # Create full_text exceeding 200 words for both papers
    full_text = " ".join(["This is a test sentence."] * 50)  # 50 sentences ~ 200 words
    return SearchResults(results=[
        SearchResult(
            doi="10.1234/test.doi1",
            authors=["Author One", "Author Two"],
            citation_count=10,
            journal="Journal of Testing",
            pdf_link="http://example.com/test1.pdf",
            publication_year=2021,
            title="Test Paper Title 1",
            full_text=full_text,
            search_query="impact of climate change",
            query_rationale="Testing impact queries"
        ),
        SearchResult(
            doi="10.5678/test.doi2",
            authors=["Author Three", "Author Four"],
            citation_count=15,
            journal="Climate Research Journal",
            pdf_link="http://example.com/test2.pdf",
            publication_year=2022,
            title="Test Paper Title 2",
            full_text=full_text,
            search_query="impact of climate change",
            query_rationale="Evaluating climate effects"
        )
    ])

@pytest.mark.asyncio
async def test_analyze_papers_ranking(mock_search_results):
    analyzer = PaperAnalyzer()
    with patch('analyze_papers.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm, \
         patch.object(analyzer, 'analyze_paper', new_callable=AsyncMock) as mock_analyze_paper:
        
        # Mock the LLMAPIHandler responses with proper structure
        mock_llm.return_value = [RankingResponse(rankings=[
            PaperRanking(paper_id="paper_0", rank=1, explanation="Highly relevant"),
            PaperRanking(paper_id="paper_1", rank=2, explanation="Less relevant"),
        ])]

        # Mock the analyze_paper method
        mock_analyze_paper.side_effect = [
            PaperAnalysis(
                analysis="This paper is highly relevant.",
                relevant_quotes=["Significant impact on climate change."]
            ),
            PaperAnalysis(
                analysis="This paper is less relevant but still important.",
                relevant_quotes=["Some impact on climate observed."]
            )
        ]

        ranked_papers = await analyzer.analyze_papers(mock_search_results, "impact of climate change")

        # Assertions
        assert len(ranked_papers.papers) == 2
        assert ranked_papers.papers[0].relevance_score > ranked_papers.papers[1].relevance_score
        assert all(paper.relevance_score > 0 for paper in ranked_papers.papers)
        
        assert ranked_papers.papers[0].analysis == "This paper is highly relevant."
        assert ranked_papers.papers[1].analysis == "This paper is less relevant but still important."
        
        assert len(ranked_papers.papers[0].relevant_quotes) == 1
        assert len(ranked_papers.papers[1].relevant_quotes) == 1
        
        assert ranked_papers.papers[0].relevant_quotes[0] == "Significant impact on climate change."
        assert ranked_papers.papers[1].relevant_quotes[0] == "Some impact on climate observed."

        # Verify that the methods were called the expected number of times
        assert mock_llm.call_count > 0
        assert mock_analyze_paper.call_count == 2

@pytest.mark.asyncio
async def test_analyze_paper_analysis(mock_search_results):
    analyzer = PaperAnalyzer()
    paper = mock_search_results.results[0]
    with patch('analyze_papers.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = [PaperAnalysis(
            analysis="This paper is highly relevant.",
            relevant_quotes=["Significant impact on climate change."]
        )]
        analysis = await analyzer.analyze_paper("impact of climate change", paper)
        assert analysis.analysis == "This paper is highly relevant."
        assert len(analysis.relevant_quotes) == 1
        assert analysis.relevant_quotes[0] == "Significant impact on climate change."