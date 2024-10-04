import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from synthesize_results import ResultSynthesizer, SynthesisResponse
from models import RankedPapers, RankedPaper

@pytest.mark.asyncio
async def test_synthesize():
    synthesizer = ResultSynthesizer()
    mock_ranked_papers = RankedPapers(papers=[
        RankedPaper(
            id="1",
            title="Test Paper",
            authors=["Author One"],
            year=2021,
            relevance_score=0.95,
            analysis="This paper discusses...",
            relevant_quotes=["Quote one"]
        )
    ])
    with patch('synthesize_results.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = [SynthesisResponse(plan="Test plan", content="Test content")]
        synthesis = await synthesizer.synthesize(mock_ranked_papers, "Impact of climate change")
        assert synthesis == "Test content"
