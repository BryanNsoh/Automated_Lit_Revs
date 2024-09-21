# searchers/arxiv_search.py
import os
import asyncio
import aiohttp
import aiofiles
import xml.etree.ElementTree as ET
from typing import List, Dict
import fitz  # PyMuPDF
import re
from aiolimiter import AsyncLimiter
import tempfile
from concurrent.futures import ThreadPoolExecutor
from asyncio import Semaphore
import time
import logging
from .searcher import Searcher
from models import SearchQueries, SearchResults, SearchResult, SearchQuery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Define the data directory
DATA_DIR = os.path.join(os.getcwd(), 'data')
PDF_DIR = os.path.join(DATA_DIR, 'pdfs')
os.makedirs(PDF_DIR, exist_ok=True)

class ArXivSearch(Searcher):
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.rate_limiter = AsyncLimiter(5, 1)  # 5 requests per second
        self.semaphore = Semaphore(5)  # Maximum 5 concurrent queries
        self.executor = ThreadPoolExecutor(max_workers=5)  # For parallel PDF processing

    async def search_and_parse_queries(self, search_queries: SearchQueries) -> SearchResults:
        results = SearchResults(results=[])
        async with aiohttp.ClientSession() as session:
            for query in search_queries.queries:
                query_results = await self.process_query(session, query)
                results.results.extend(query_results)
                if len(results.results) >= self.max_results:
                    break
        
        return SearchResults(results=results.results[:self.max_results])

    async def process_query(self, session: aiohttp.ClientSession, query: SearchQuery) -> List[SearchResult]:
        async with self.semaphore:
            arxiv_results = await self.search(session, query.search_query)
            results = []
            for paper in arxiv_results:
                full_text = await self.get_full_text(session, paper['pdf_url'], paper['id'])
                result = SearchResult(
                    DOI=paper.get('doi', ''),
                    authors=paper['authors'],
                    citation_count=0,  # arXiv doesn't provide citation count
                    journal=paper.get('journal_ref', '') or '',
                    pdf_link=paper['pdf_url'],
                    publication_year=int(paper['published'][:4]),
                    title=paper['title'],
                    full_text=full_text,
                    search_query=query.search_query,
                    query_rationale=query.query_rationale
                )
                results.append(result)
            return results

    async def search(self, session: aiohttp.ClientSession, search_query: str) -> List[Dict]:
        base_url = 'http://export.arxiv.org/api/query?'
        query_url = f'search_query=all:{search_query}&start=0&max_results={self.max_results}&sortBy=relevance&sortOrder=descending'
        full_url = base_url + query_url

        async with self.rate_limiter:
            async with session.get(full_url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {full_url}: Status {response.status}")
                    return []
                xml_data = await response.text()

        return self.parse_metadata(xml_data)

    def parse_metadata(self, xml_data: str) -> List[Dict]:
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            logger.error(f"Error parsing XML data: {e}")
            return []

        ns = {'arxiv': 'http://www.w3.org/2005/Atom', 'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'}
        papers = []
        for entry in root.findall('arxiv:entry', ns):
            primary_category = entry.find('arxiv:primary_category', ns)
            paper = {
                'id': entry.find('arxiv:id', ns).text,
                'title': entry.find('arxiv:title', ns).text.strip(),
                'authors': [author.find('arxiv:name', ns).text for author in entry.findall('arxiv:author', ns)],
                'summary': entry.find('arxiv:summary', ns).text.strip(),
                'published': entry.find('arxiv:published', ns).text,
                'updated': entry.find('arxiv:updated', ns).text,
                'pdf_url': entry.find('arxiv:link[@title="pdf"]', ns).attrib['href'],
                'doi': entry.find('arxiv:doi', ns).text if entry.find('arxiv:doi', ns) is not None else None,
                'journal_ref': entry.find('arxiv:journal_ref', ns).text if entry.find('arxiv:journal_ref', ns) is not None else None,
                'primary_category': primary_category.attrib['term'] if primary_category is not None else None,
                'categories': ','.join([category.attrib['term'] for category in entry.findall('arxiv:category', ns)])
            }
            papers.append(paper)
        return papers

    async def get_full_text(self, session: aiohttp.ClientSession, pdf_url: str, arxiv_id: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            pdf_path = temp_file.name

        try:
            await self.download_pdf(session, pdf_url, pdf_path)
            return await self.extract_text_from_pdf(pdf_path)
        finally:
            os.unlink(pdf_path)  # Delete the temporary file

    async def download_pdf(self, session: aiohttp.ClientSession, pdf_url: str, pdf_path: str) -> None:
        async with self.rate_limiter:
            try:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        async with aiofiles.open(pdf_path, mode='wb') as f:
                            await f.write(content)
                    else:
                        logger.warning(f"Failed to download PDF: Status {response.status}")
            except Exception as e:
                logger.error(f"Exception while downloading PDF: {e}")

    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(self.executor, self._extract_text, pdf_path)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def _extract_text(self, pdf_path: str) -> str:
        with fitz.open(pdf_path) as doc:
            return "".join(page.get_text() for page in doc)

# Ensure the ArXivSearch class is exported
__all__ = ['ArXivSearch']