from typing import List, Optional, Dict 
from pydantic import BaseModel, Field

class Paper(BaseModel):
    id: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_year: Optional[int] = None
    abstract: Optional[str] = None
    full_text: Optional[str] = None

class RankedPaper(Paper):
    relevance_score: float = 0.0
    analysis: str = ""
    relevant_quotes: List[str] = Field(default_factory=list)
    bibtex: Optional[str] = None
    
class RankedPapers(BaseModel):
    papers: List[RankedPaper] = Field(default_factory=list)

class SearchQuery(BaseModel):
    search_query: str
    query_rationale: str
    
class SearchQueries(BaseModel):
    queries: List[SearchQuery]

class SearchResult(BaseModel):
    doi: Optional[str] = ""
    authors: List[str] = []
    citation_count: int = 0
    journal: str = ""
    pdf_link: str = ""
    publication_year: Optional[int] = None
    title: str = ""
    full_text: str = ""
    search_query: str = ""
    query_rationale: str = ""
class SearchResults(BaseModel):
    results: List[SearchResult] = []

class PaperAnalysis(BaseModel):
    analysis: str
    relevant_quotes: List[str]

class RankedPaperResult(BaseModel):
    paper: SearchResult
    relevance_score: float
    analysis: str
    relevant_quotes: List[str]
    bibtex: Optional[str] = None

class PaperRanking(BaseModel):
    paper_id: str
    rank: int
    explanation: str

class RankingResponse(BaseModel):
    rankings: List[PaperRanking]

class SynthesisResponse(BaseModel):
    plan: str
    content: str