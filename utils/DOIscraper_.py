import asyncio
import random
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class DOIScraper:
    def __init__(self):
        self.driver = None

    async def initialize_webdriver(self):
        options = uc.ChromeOptions()
        options.add_argument("--blink-settings=imagesEnabled=false")

        # Generate a random user agent
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f"user-agent={user_agent}")

        self.driver = uc.Chrome(options=options)

    async def navigate_to_doi_link(self, doi_link):
        self.driver.get(doi_link)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            pass
        await asyncio.sleep(3)  # Add a delay to avoid overwhelming the website

    async def extract_text_content(self):
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            text_content = body.text
            return text_content.replace("\n", " ")
        except (NoSuchElementException, TimeoutException):
            return ""

    async def get_doi_content(self, doi_link):
        await self.initialize_webdriver()
        await self.navigate_to_doi_link(doi_link)
        content = await self.extract_text_content()
        self.driver.quit()

        # Check if the content contains any of the specified strings
        if any(
            s in content
            for s in [
                "! There was a problem providing the content you requested Please contact us via our support center for more information and provide the details below.",
                "The requested URL was rejected. Please consult with your administrator.",
            ]
        ):
            return ""

        return content


async def main():
    scraper = DOIScraper()
    doi_link = "https://doi.org/10.1016/j.engappai.2024.107881"
    content = await scraper.get_doi_content(doi_link)
    print(content)


asyncio.run(main())
