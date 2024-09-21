# searchers/searcher.py
from abc import ABC, abstractmethod
from models import SearchQueries, SearchResults

class Searcher(ABC):
    @abstractmethod
    async def search_and_parse_queries(self, search_queries: SearchQueries) -> SearchResults:
        pass