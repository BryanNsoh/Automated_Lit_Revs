import asyncio
from pyppeteer import launch
from fake_useragent import UserAgent


class DOIScraper:
    def __init__(self, max_browsers=5):
        self.max_browsers = max_browsers
        self.browser_pool = asyncio.Queue(maxsize=max_browsers)
        self.semaphore = asyncio.Semaphore(max_browsers)
        self.active_tasks = set()

    async def initialize_browser_pool(self):
        for _ in range(self.max_browsers):
            browser = await launch(headless=True, args=["--no-sandbox"])
            await self.browser_pool.put(browser)

    async def close_browser_pool(self):
        while not self.browser_pool.empty():
            browser = await self.browser_pool.get()
            await browser.close()

    async def get_browser(self):
        return await self.browser_pool.get()

    async def release_browser(self, browser):
        await self.browser_pool.put(browser)

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
                browser = await self.get_browser()
                page = await browser.newPage()
                await self.navigate_to_doi_link(page, doi_link)
                content = await self.extract_text_content(page)
                await page.close()
                await self.release_browser(browser)

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
        task = asyncio.create_task(self.get_doi_content(doi_link))
        self.active_tasks.add(task)
        result = await task
        self.active_tasks.remove(task)
        return result

    async def run(self, doi_link):
        if not self.browser_pool.full():
            await self.initialize_browser_pool()
        result = await self.scrape_doi_link(doi_link)
        if self.browser_pool.empty() and len(self.active_tasks) == 0:
            await self.close_browser_pool()
        return result


async def main():
    scraper = DOIScraper(max_browsers=3)
    doi_link = "10.1016/j.engappai.2024.107881"
    result = await scraper.run(doi_link)
    print(f"Result: {result}")


asyncio.run(main())
