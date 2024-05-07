import asyncio
import random
import aiohttp
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
import logging
import sys


class WebScraper:
    def __init__(self, session, max_concurrent_tasks=120):
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.user_agent = UserAgent()
        self.browser = None
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.logger.info("Browser initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def close(self):
        if self.browser:
            await self.browser.close()
            self.logger.info("Browser closed")

    async def scrape_url(self, url, max_retries=3):
        if not self.browser:
            await self.initialize()  # Ensure the browser is initialized

        retry_count = 0
        while retry_count < max_retries:
            try:
                context = await self.browser.new_context(
                    user_agent=self.user_agent.random,
                    viewport={"width": 1920, "height": 1080},
                    ignore_https_errors=True,
                )
                page = await context.new_page()
                await self.navigate_to_url(page, url)
                content = await self.extract_text_content(page)
                self.logger.info(f"Successfully scraped URL: {url}")
                await page.close()
                await context.close()
                return content
            except Exception as e:
                self.logger.error(
                    f"Error occurred while scraping URL: {url}. Error: {str(e)}"
                )
                retry_count += 1
                await asyncio.sleep(
                    random.uniform(1, 5)
                )  # Random delay between retries
            finally:
                try:
                    await page.close()
                    await context.close()
                except Exception as e:
                    self.logger.warning(
                        f"Error occurred while closing page or context: {str(e)}"
                    )
        self.logger.warning(f"Max retries exceeded for URL: {url}")
        return ""

    async def get_url_content(self, url):
        async with self.semaphore:
            return await self.scrape_url(url)

    async def navigate_to_url(self, page, url, max_retries=3):
        if not url.startswith("http"):
            url = f"https://doi.org/{url}"
        retry_count = 0
        while retry_count < max_retries:
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(1)  # Minor delay to ensure page loads completely
                return
            except Exception as e:
                self.logger.warning(
                    f"Retrying URL: {url}. Remaining retries: {max_retries - retry_count}"
                )
                retry_count += 1
                await asyncio.sleep(
                    random.uniform(1, 5)
                )  # Random delay between retries
        self.logger.error(
            f"Failed to navigate to URL: {url} after {max_retries} retries"
        )
        raise e

    async def extract_text_content(self, page):
        try:
            paragraphs = await page.query_selector_all("p")
            text_content = "".join(
                [await paragraph.inner_text() + "\n" for paragraph in paragraphs]
            )
            return text_content.strip()
        except Exception as e:
            self.logger.error(f"Failed to extract text content. Error: {str(e)}")
            return ""


# Usage
async def main():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("scraper.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    async with aiohttp.ClientSession() as session:
        scraper = WebScraper(session=session)
        try:
            await scraper.initialize()
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            return  # Early return if initialization fails

        urls = [
            "10.1016/j.ifacol.2020.12.237",
            "10.1016/j.agwat.2023.108536",
            "10.1016/j.atech.2023.100251",
            "10.1016/j.atech.2023.100179",
            "10.1016/j.ifacol.2023.10.677",
            "10.1016/j.ifacol.2023.10.1655",
            "10.1016/j.ifacol.2023.10.667",
            "10.1002/cjce.24764",
            "10.3390/app13084734",
            "10.1016/j.atech.2022.100074",
            "10.1007/s10668-023-04028-9",
            "10.1109/IJCNN54540.2023.10191862",
            "10.1201/9780429290152-5",
            "10.1016/j.jprocont.2022.10.003",
            "10.1016/j.rser.2022.112790",
            "10.1007/s11269-022-03191-4",
            "10.3390/app12094235",
            "10.3390/w14060889",
            "10.3390/su14031304",
        ]

        scrape_tasks = []
        for url in urls:
            scrape_task = asyncio.create_task(scraper.get_url_content(url))
            scrape_tasks.append(scrape_task)

        scraped_contents = await asyncio.gather(*scrape_tasks)

        for url, content in zip(urls, scraped_contents):
            logging.info(f"Scraped content for URL: {url}")
            logging.info(f"Content: {content}")

        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
