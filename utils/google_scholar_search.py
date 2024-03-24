import requests
import yaml
from bs4 import BeautifulSoup
import logging
import time
import random

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class GoogleScholarScraper:
    def __init__(self, yaml_file, max_requests_per_minute=30, delay_range=(1, 5)):
        self.yaml_file = yaml_file
        self.max_requests_per_minute = max_requests_per_minute
        self.delay_range = delay_range
        self.request_count = 0
        self.last_request_time = time.time()

    async def get_scholar_data(self, query):
        try:
            # Rate limiting
            current_time = time.time()
            elapsed_time = current_time - self.last_request_time
            if elapsed_time < 60 / self.max_requests_per_minute:
                sleep_time = 60 / self.max_requests_per_minute - elapsed_time
                logging.info(f"Rate limiting: Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            self.last_request_time = time.time()

            # Random delay
            delay = random.uniform(*self.delay_range)
            logging.info(f"Random delay: Sleeping for {delay:.2f} seconds")
            time.sleep(delay)

            url = f"https://www.google.com/scholar?q={query}&hl=en"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
            }
            logging.info(f"Sending request to URL: {url}")
            response = requests.get(url, headers=headers)
            logging.info(f"Received response with status code: {response.status_code}")
            soup = BeautifulSoup(response.text, "html.parser")
            scholar_results = []
            for el in soup.select(".gs_ri"):
                title = el.select(".gs_rt")[0].text if el.select(".gs_rt") else ""
                doi = (
                    el.select(".gs_a a[href*='doi.org']")[0].text
                    if el.select(".gs_a a[href*='doi.org']")
                    else ""
                )
                full_text = ""
                inline_citation = ""  # Not available in the provided HTML structure
                full_citation = ""  # Not available in the provided HTML structure
                publication_year = (
                    el.select(".gs_a")[0].text.split(" - ")[-1]
                    if " - " in el.select(".gs_a")[0].text
                    else ""
                )
                authors = (
                    [
                        author.strip()
                        for author in el.select(".gs_a")[0]
                        .text.split(" - ")[0]
                        .split(",")
                    ]
                    if " - " in el.select(".gs_a")[0].text
                    else []
                )
                citation_count = (
                    int(
                        el.select(".gs_fl a:contains('Cited by')")[0].text.split(" ")[
                            -1
                        ]
                    )
                    if el.select(".gs_fl a:contains('Cited by')")
                    else 0
                )
                pdf_link = (
                    el.select(".gs_or_ggsm a")[0]["href"]
                    if el.select(".gs_or_ggsm a")
                    else ""
                )
                journal = (
                    el.select(".gs_a")[0].text.split(" - ")[1]
                    if len(el.select(".gs_a")[0].text.split(" - ")) > 1
                    else ""
                )
                # remove "[HTML][HTML]" and "[PDF][PDF]" and "[BOOK][B]" from the title if present
                title = (
                    title.replace("[HTML][HTML]", "")
                    .replace("[PDF][PDF]", "")
                    .replace("[BOOK][B]", "")
                )
                scholar_results.append(
                    {
                        "title": title,
                        "DOI": doi,
                        "full_text": full_text,
                        "inline_citation": inline_citation,
                        "full_citation": full_citation,
                        "publication_year": publication_year,
                        "authors": authors,
                        "citation_count": citation_count,
                        "pdf_link": pdf_link,
                        "journal": journal,
                    }
                )
            logging.info(
                f"Extracted {len(scholar_results)} scholar results for query: {query}"
            )
            return scholar_results
        except Exception as e:
            logging.error(f"Error occurred while processing query: {query}")
            logging.error(f"Exception: {str(e)}")
            return None

    async def process_queries(self):
        with open(self.yaml_file, "r") as file:
            data = yaml.safe_load(file)
            print(f"Loaded YAML file: {self.yaml_file}")

    async def process_queries(self):
        with open(self.yaml_file, "r") as file:
            data = yaml.safe_load(file)

        for subsection in data["subsections"]:
            for point in subsection["points"]:
                point_title = next(iter(point))
                print(f"Processing point: {point_title}")

                if "google_queries" in point[point_title]:
                    for query_data in point[point_title]["google_queries"]:
                        if query_data["query_id"].startswith("google_"):
                            query = query_data["query"]
                            logging.info(f"Processing Google query: {query}")
                            results = await self.get_scholar_data(query)
                            query_data["responses"] = results
                            logging.info(f"Processed Google query: {query}")

                if "scopus_queries" in point[point_title]:
                    for query_data in point[point_title]["scopus_queries"]:
                        if query_data["query_id"].startswith("scopus_"):
                            query = query_data["query"]
                            logging.info(f"Processing Scopus query: {query}")
                            # Perform Scopus query processing here
                            logging.info(f"Processed Scopus query: {query}")

        with open(self.yaml_file, "w") as file:
            yaml.dump(data, file)
        logging.info(f"Updated YAML file: {self.yaml_file}")


async def main():
    yaml_file = "data.yaml"
    scraper = GoogleScholarScraper(
        yaml_file, max_requests_per_minute=30, delay_range=(1, 5)
    )
    logging.info("Starting Google Scholar scraper")
    await scraper.process_queries()
    logging.info("Google Scholar scraping completed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
