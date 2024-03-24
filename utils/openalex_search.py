import aiohttp
import asyncio
import json
import fitz


class OpenAlexPaperSearch:
    def __init__(self, email, doi_scraper):
        self.base_url = "https://api.openalex.org"
        self.email = email
        self.doi_scraper = doi_scraper

    async def search_papers(self, query, max_results=30):
        async with aiohttp.ClientSession() as session:
            search_url = f"{self.base_url}/works?search={query}&per_page={max_results}&mailto={self.email}"
            async with session.get(search_url) as resp:
                data = await resp.json()
                paper_data = []
                for work in data["results"]:
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
                            and "source" in work["primary_location"]
                            else ""
                        ),
                        "pdf_link": (
                            work["primary_location"]["pdf_url"]
                            if "primary_location" in work
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
                        paper["full_text"] = await self.extract_fulltext(
                            paper["pdf_link"]
                        )
                    elif paper["DOI"]:
                        paper["full_text"] = await self.extract_fulltext_from_doi(
                            paper["DOI"]
                        )
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

    async def extract_fulltext_from_doi(self, doi):
        try:
            content = await self.doi_scraper.get_doi_content(doi)
            return content
        except Exception as e:
            print(f"Error: Failed to scrape full text from DOI {doi}. {str(e)}")
            return ""


async def main():
    from doi_scraper import DOIScraper

    doi_scraper = DOIScraper()
    searcher = OpenAlexPaperSearch(
        email="your_email@example.com", doi_scraper=doi_scraper
    )
    query = '"sensor data fusion" "irrigation optimization" "machine learning"'
    results = await searcher.search_papers(query)
    with open("openalex_results.json", "w") as file:
        file.write(results)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
