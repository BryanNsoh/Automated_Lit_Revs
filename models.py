from dataclasses import dataclass, field
from typing import List, Optional, Dict 
from pydantic import BaseModel, Field

@dataclass
class Paper:
    id: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    full_text: Optional[str] = None

@dataclass
class RankedPaper(Paper):
    relevance_score: float = 0.0
    analysis: str = ""
    relevant_quotes: List[str] = field(default_factory=list)
    bibtex: Optional[str] = None
    
@dataclass
class RankedPapers:
    papers: List[RankedPaper] = field(default_factory=list)

@dataclass
class SearchQuery:
    search_query: str
    query_rationale: str
    
@dataclass  
class SearchQueries:
    queries: Dict[str, SearchQuery]

@dataclass
class SearchResult:
    DOI: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    citation_count: int = 0
    journal: Optional[str] = None
    pdf_link: Optional[str] = None
    publication_year: Optional[int] = None
    title: Optional[str] = None
    query_rationale: Optional[str] = None

@dataclass
class SearchResults:
    results: Dict[str, SearchResult] = field(default_factory=dict)

class PaperAnalysis(BaseModel):
    analysis: str
    relevant_quotes: List[str]

@dataclass
class RankedPaperResult:
    paper: SearchResult
    relevance_score: float
    analysis: str
    relevant_quotes: List[str]
    bibtex: Optional[str] = None