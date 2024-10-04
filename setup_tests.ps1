# setup_tests.ps1

# Function to check if an item exists in an array
function Contains($array, $item) {
    return $array -contains $item
}

# 1. Add testing dependencies to requirements.txt if not already present
$test_dependencies = @("pytest", "pytest-asyncio", "pytest-mock")
$requirements_path = ".\requirements.txt"

if (Test-Path $requirements_path) {
    $requirements = Get-Content -Path $requirements_path
    foreach ($dep in $test_dependencies) {
        if (-not (Contains $requirements $dep)) {
            Add-Content -Path $requirements_path -Value $dep
            Write-Host "Added `$dep` to `requirements.txt`"
        }
        else {
            Write-Host "`$dep` already exists in `requirements.txt`"
        }
    }
}
else {
    Write-Error "`requirements.txt` not found in the repository root."
    exit 1
}

# 2. Create tests directory structure
$tests_dir = ".\tests"
$searchers_tests_dir = ".\tests\searchers"

# Create main tests directory
if (-not (Test-Path $tests_dir)) {
    New-Item -Path $tests_dir -ItemType Directory | Out-Null
    Write-Host "Created `tests` directory."
}
else {
    Write-Host "`tests` directory already exists."
}

# Create searchers subdirectory within tests
if (-not (Test-Path $searchers_tests_dir)) {
    New-Item -Path $searchers_tests_dir -ItemType Directory | Out-Null
    Write-Host "Created `tests\searchers` directory."
}
else {
    Write-Host "`tests\searchers` directory already exists."
}

# 3. Create __init__.py files in tests directories
Set-Content -Path "$tests_dir\__init__.py" -Value ""
Set-Content -Path "$searchers_tests_dir\__init__.py" -Value ""

# 4. Define test file contents

# test_analyze_papers.py
$test_analyze_papers = @"
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from analyze_papers import PaperAnalyzer
from models import SearchResults, SearchResult, RankedPapers, PaperAnalysis

@pytest.fixture
def mock_search_results():
    # Create a full_text exceeding 200 words
    full_text = " ".join(["This is a test sentence."] * 50)  # 50 sentences ~ 200 words
    return SearchResults(results=[
        SearchResult(
            doi="10.1234/test.doi",
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
        # Mock the LLMAPIHandler responses with proper structure
        mock_llm.return_value = [
            {
                "rankings": [
                    {"paper_id": "paper_0", "rank": 1, "explanation": "Highly relevant"},
                ],
                "analysis": "This paper is highly relevant.",
                "relevant_quotes": ["Significant impact on climate change."]
            }
        ]
        ranked_papers = await analyzer.analyze_papers(mock_search_results, "impact of climate change")
        assert len(ranked_papers.papers) == 1
        assert ranked_papers.papers[0].relevance_score > 0
        assert ranked_papers.papers[0].analysis == "This paper is highly relevant."
        assert len(ranked_papers.papers[0].relevant_quotes) == 1

@pytest.mark.asyncio
async def test_analyze_paper_analysis(mock_search_results):
    analyzer = PaperAnalyzer()
    paper = mock_search_results.results[0]
    with patch('analyze_papers.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = [
            {
                "analysis": "This paper is highly relevant.",
                "relevant_quotes": ["Significant impact on climate change."]
            }
        ]
        analysis = await analyzer.analyze_paper("impact of climate change", paper)
        assert analysis.analysis == "This paper is highly relevant."
        assert len(analysis.relevant_quotes) == 1
        assert analysis.relevant_quotes[0] == "Significant impact on climate change."
"@

# test_get_search_queries.py
$test_get_search_queries = @"
import pytest
from unittest.mock import AsyncMock, patch
from get_search_queries import QueryGenerator
from models import SearchQueries, SearchQuery

@pytest.mark.asyncio
async def test_generate_queries():
    generator = QueryGenerator()
    with patch('get_search_queries.LLMAPIHandler.async_process', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = [
            SearchQueries(queries=[
                SearchQuery(search_query="climate change AND water resources", query_rationale="Testing rationale 1"),
                SearchQuery(search_query="water scarcity AND hydrologist", query_rationale="Testing rationale 2"),
                SearchQuery(search_query="sea level rise AND coastal erosion", query_rationale="Testing rationale 3"),
                SearchQuery(search_query="water conservation AND climate mitigation", query_rationale="Testing rationale 4"),
                SearchQuery(search_query="glacier melting AND cryosphere", query_rationale="Testing rationale 5"),
            ])
        ]
        queries = await generator.generate_queries("impact of climate change on water resources", 5)
        assert len(queries.queries) == 5
        assert queries.queries[0].search_query == "climate change AND water resources"
"@

# test_llm_api_handler.py
$test_llm_api_handler = @"
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from llm_api_handler import LLMAPIHandler
from models import RankingResponse, PaperAnalysis

@pytest.mark.asyncio
async def test_async_process_regular():
    handler = LLMAPIHandler()
    with patch.object(handler.async_openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_message = MagicMock()
        mock_message.content = 'Test response'
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_create.return_value.choices = [mock_choice]
        response = await handler.async_process(
            prompts=["What's the capital of France?"],
            model="gpt-4o-mini",
            system_message="You are a helpful assistant.",
            temperature=0.7,
            response_format=None
        )
        assert response == ["Test response"]

@pytest.mark.asyncio
async def test_async_process_structured_response():
    handler = LLMAPIHandler()
    with patch.object(handler.async_openai_client.beta.chat.completions, 'parse', new_callable=AsyncMock) as mock_parse:
        mock_message = MagicMock()
        mock_message.parsed = {"answer": "Paris", "confidence": 0.99}
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_parse.return_value.choices = [mock_choice]
        from pydantic import BaseModel

        class ResponseModel(BaseModel):
            answer: str
            confidence: float

        response = await handler.async_process(
            prompts=["What's the capital of France?"],
            model="gpt-4o-mini",
            system_message=None,
            temperature=0.7,
            response_format=ResponseModel
        )
        # Determine the type of response (begin by printing it)
        print(type(response))
        # Print the content of the response
        print(response)
        assert isinstance(response[0], ResponseModel)
        assert response[0].answer == "Paris"
        assert response[0].confidence == 0.99
"@

# test_logger_config.py
$test_logger_config = @"
import pytest
from logger_config import get_logger

def test_get_logger():
    logger = get_logger("test_module")
    assert logger.name == "test_module"
"@

# test_misc_utils.py
$test_misc_utils = @"
import pytest
from unittest.mock import patch
from misc_utils import get_api_keys

@patch('os.getenv')
def test_get_api_keys(mock_getenv):
    mock_getenv.side_effect = lambda key: 'test_key' if 'API_KEY' in key else None
    keys = get_api_keys()
    assert keys['OPENAI_API_KEY'] == 'test_key'
    assert keys['CORE_API_KEY'] == 'test_key'
"@

# test_models.py
$test_models = @"
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
"@

# test_synthesize_results.py
$test_synthesize_results = @"
import pytest
from unittest.mock import AsyncMock, patch
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
"@

# test_arxiv_search.py
$test_arxiv_search = @"
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
"@

# test_core_search.py
$test_core_search = @"
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
"@

# test_searcher.py
$test_searcher = @"
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
"@

# 5. Create test files with the defined content
Set-Content -Path "$tests_dir\test_analyze_papers.py" -Value $test_analyze_papers
Set-Content -Path "$tests_dir\test_get_search_queries.py" -Value $test_get_search_queries
Set-Content -Path "$tests_dir\test_llm_api_handler.py" -Value $test_llm_api_handler
Set-Content -Path "$tests_dir\test_logger_config.py" -Value $test_logger_config
Set-Content -Path "$tests_dir\test_misc_utils.py" -Value $test_misc_utils
Set-Content -Path "$tests_dir\test_models.py" -Value $test_models
Set-Content -Path "$tests_dir\test_synthesize_results.py" -Value $test_synthesize_results
Set-Content -Path "$searchers_tests_dir\test_arxiv_search.py" -Value $test_arxiv_search
Set-Content -Path "$searchers_tests_dir\test_core_search.py" -Value $test_core_search
Set-Content -Path "$searchers_tests_dir\test_searcher.py" -Value $test_searcher

Write-Host "✅ Unit tests have been set up successfully."

# 6. Apply necessary code corrections

# Update analyze_papers.py to fix attribute access
$analyze_papers_content = Get-Content -Path ".\analyze_papers.py" -Raw

# Replace 'year=result.year' with 'year=result.publication_year'
$analyze_papers_content = $analyze_papers_content -replace 'year=result\.year', 'year=result.publication_year'

# Replace any 'paper.year' with 'paper.publication_year'
$analyze_papers_content = $analyze_papers_content -replace 'paper\.year', 'paper.publication_year'

Set-Content -Path ".\analyze_papers.py" -Value $analyze_papers_content

Write-Host "✅ Code corrections have been applied."
