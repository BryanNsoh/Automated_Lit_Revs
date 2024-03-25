import aiohttp
import asyncio
import json
import fitz
import urllib.parse
from misc_utils import prepare_text_for_json


class OpenAlexPaperSearch:
    def __init__(self, email, web_scraper):
        self.base_url = "https://api.openalex.org"
        self.email = email
        self.web_scraper = web_scraper

    async def search_papers(self, query, max_results=30):
        async with aiohttp.ClientSession() as session:
            if query.startswith("https://api.openalex.org/works?"):
                search_url = f"{query}&mailto={self.email}"
            else:
                encoded_query = urllib.parse.quote(query)
                search_url = f"{self.base_url}/works?search={encoded_query}&per_page={max_results}&mailto={self.email}"
            async with session.get(search_url) as resp:
                data = await resp.json()
                print(data)
                paper_data = []
                for work in data["results"][:25]:
                    paper = {
                        "DOI": work["doi"] if "doi" in work else "",
                        "authors": (
                            [
                                author["author"]["display_name"]
                                for author in work["authorships"]
                            ]
                            if "authorships" in work
                            else []
                        ),
                        "citation_count": (
                            work["cited_by_count"] if "cited_by_count" in work else 0
                        ),
                        "full_citation": "",
                        "full_text": "",
                        "analysis": "",
                        "verbatim_quote1": "",
                        "verbatim_quote2": "",
                        "verbatim_quote3": "",
                        "relevance_score1": 0,
                        "relevance_score2": 0,
                        "limitations": "",
                        "inline_citation": "",
                        "journal": (
                            work["primary_location"]["source"]["display_name"]
                            if "primary_location" in work
                            and isinstance(work["primary_location"], dict)
                            and "source" in work["primary_location"]
                            and isinstance(work["primary_location"]["source"], dict)
                            and "display_name" in work["primary_location"]["source"]
                            else ""
                        ),
                        "pdf_link": (
                            work["primary_location"]["pdf_url"]
                            if "primary_location" in work
                            and isinstance(work["primary_location"], dict)
                            and "pdf_url" in work["primary_location"]
                            else ""
                        ),
                        "publication_year": (
                            work["publication_year"]
                            if "publication_year" in work
                            else ""
                        ),
                        "title": work["title"] if "title" in work else "",
                    }
                    if paper["pdf_link"]:
                        full_text = await self.extract_fulltext(paper["pdf_link"])
                        if not paper["full_text"]:
                            full_text = await self.extract_fulltext_from_url(
                                paper["pdf_link"]
                            )
                    if not paper["full_text"] and paper["DOI"]:
                        full_text = await self.extract_fulltext_from_doi(paper["DOI"])

                    if full_text:
                        paper["full_text"] = await prepare_text_for_json(full_text)

                    paper_data.append(paper)
                return json.dumps(paper_data, indent=2)

    async def extract_fulltext(self, pdf_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as resp:
                pdf_bytes = await resp.read()
                try:
                    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                        fulltext = ""
                        for page in doc:
                            fulltext += page.get_text()
                        return fulltext
                except fitz.FileDataError:
                    print(f"Error: Cannot open PDF file from {pdf_url}")
                    return ""

    async def extract_fulltext_from_url(self, pdf_url):
        try:
            content = await self.web_scraper.get_url_content(pdf_url)
            return content
        except Exception as e:
            print(f"Error: Failed to scrape full text from PDF URL {pdf_url}. {str(e)}")
            return ""

    async def extract_fulltext_from_doi(self, doi):
        try:
            content = await self.web_scraper.get_url_content(doi)
            return content
        except Exception as e:
            print(f"Error: Failed to scrape full text from DOI {doi}. {str(e)}")
            return ""


async def main():
    from web_scraper import WebScraper

    web_scraper = WebScraper()
    searcher = OpenAlexPaperSearch(
        email="your_email@example.com", web_scraper=web_scraper
    )

    queries = [
        'https://api.openalex.org/works?search="MQTT+protocol"+"real-time"+"smart+irrigation+system"&sort=relevance_score:desc&per_page=50',
    ]

    for query in queries:
        results = await searcher.search_papers(query)
        with open(f"openalex_results_{queries.index(query)}.json", "w") as file:
            file.write(results)
        print(results)


if __name__ == "__main__":
    asyncio.run(main())
