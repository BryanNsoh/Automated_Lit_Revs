import pytest
from pydantic import ValidationError
from models import Paper, RankedPaper, SearchQuery, SearchResult

def test_paper_model():
    paper = Paper(
        id="1",
        doi="10.1234/test.doi",
        title="Test Paper",
        authors=["Author One"],
        year=2021,
        abstract="Test abstract",
        full_text="Test full text"
    )
    assert paper.title == "Test Paper"

def test_ranked_paper_model():
    ranked_paper = RankedPaper(
        id="1",
        title="Ranked Test Paper",
        relevance_score=0.95,
        analysis="Test analysis",
        relevant_quotes=["Quote one"]
    )
    assert ranked_paper.relevance_score == 0.95

def test_search_query_model_validation():
    with pytest.raises(ValidationError):
        SearchQuery(search_query=None, query_rationale="No search query")
