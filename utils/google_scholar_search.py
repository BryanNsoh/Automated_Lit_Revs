import requests
from bs4 import BeautifulSoup


class GoogleScholarScraper:
    async def get_scholar_data(self, query):
        try:
            url = f"https://www.google.com/scholar?q={query}&hl=en"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            print(soup)
            scholar_results = []
            for el in soup.select(".gs_ri"):
                scholar_results.append(
                    {
                        "title": el.select(".gs_rt")[0].text,
                        "title_link": el.select(".gs_rt a")[0]["href"],
                        "id": el.select(".gs_rt a")[0]["id"],
                        "displayed_link": el.select(".gs_a")[0].text,
                        "snippet": el.select(".gs_rs")[0].text.replace("\n", ""),
                        "cited_by_count": el.select(".gs_nph+ a")[0].text,
                        "cited_link": "https://scholar.google.com"
                        + el.select(".gs_nph+ a")[0]["href"],
                        "versions_count": el.select("a~ a+ .gs_nph")[0].text,
                        "versions_link": (
                            "https://scholar.google.com"
                            + el.select("a~ a+ .gs_nph")[0]["href"]
                            if el.select("a~ a+ .gs_nph")[0].text
                            else ""
                        ),
                    }
                )
            for i in range(len(scholar_results)):
                scholar_results[i] = {
                    key: value
                    for key, value in scholar_results[i].items()
                    if value != "" and value is not None
                }
            return scholar_results
        except Exception as e:
            print(e)
            return None


# Sample function call
async def main():
    scraper = GoogleScholarScraper()
    query = "the rise of techno gnosticism"
    results = await scraper.get_scholar_data(query)
    print(results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
