import asyncio
from pyppeteer import launch
from fake_useragent import UserAgent


class DOIScraper:
    def __init__(self, max_concurrent_browsers=10, executable_path=None):
        self.semaphore = asyncio.Semaphore(max_concurrent_browsers)
        self.executable_path = executable_path

    async def update_user_agent(self, page):
        ua = UserAgent()
        user_agent = ua.random
        await page.setUserAgent(user_agent)

    async def navigate_to_doi_link(self, page, doi_link):
        doi_link = f"https://doi.org/{doi_link}"
        await self.update_user_agent(page)
        await page.goto(doi_link, {"waitUntil": "networkidle0"})
        await asyncio.sleep(1)

    async def extract_text_content(self, page):
        try:
            content = await page.evaluate("document.body.textContent")
            return " ".join(content.split())
        except:
            return ""

    async def get_doi_content(self, doi_link):
        async with self.semaphore:
            try:
                browser = await launch(
                    headless=True,
                    args=["--no-sandbox"],
                    executablePath=self.executable_path,
                )
                page = await browser.newPage()
                await self.navigate_to_doi_link(page, doi_link)
                content = await self.extract_text_content(page)
                await page.close()
                await browser.close()
                if any(
                    s in content
                    for s in [
                        "! There was a problem providing the content you requested Please contact us via our support center for more information and provide the details below.",
                        "The requested URL was rejected. Please consult with your administrator.",
                    ]
                ):
                    return ""
                return content
            except Exception as e:
                print(f"Error occurred while scraping DOI: {doi_link}")
                print(f"Error details: {str(e)}")
                return ""

    async def scrape_doi_link(self, doi_link):
        return await self.get_doi_content(doi_link)

    async def run(self, doi_link):
        return await self.scrape_doi_link(doi_link)


# async def main():
#     executable_path = r"C:\Users\bnsoh2\Downloads\chromedriver_win32\chromedriver.exe"  # Replace with the actual path to your Chromium executable
#     scraper = DOIScraper(max_concurrent_browsers=10, executable_path=executable_path)
#     doi_link = "10.1016/j.engappai.2024.107881"
#     result = await scraper.run(doi_link)
#     print(f"Result: {result}")


# asyncio.run(main())
