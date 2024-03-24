import asyncio
import random
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class DOIScraper:
    def __init__(self, max_drivers=5):
        self.driver_pool = asyncio.Queue(maxsize=max_drivers)
        self.semaphore = asyncio.Semaphore(max_drivers)
        self.initialize_driver_pool()

    def initialize_driver_pool(self):
        for _ in range(self.driver_pool.maxsize):
            options = uc.ChromeOptions()
            options.add_argument("--blink-settings=imagesEnabled=false")
            options.add_argument("--headless")  # Run Chrome in headless mode
            driver = uc.Chrome(options=options)
            self.driver_pool.put_nowait(driver)

    async def get_driver(self):
        return await self.driver_pool.get()

    async def release_driver(self, driver):
        await self.driver_pool.put(driver)

    async def update_user_agent(self, driver):
        ua = UserAgent()
        user_agent = ua.random
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": user_agent}
        )

    async def navigate_to_doi_link(self, driver, doi_link):
        doi_link = f"https://doi.org/{doi_link}"
        await self.update_user_agent(driver)  # Update the user agent before navigating
        driver.get(doi_link)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            pass
        await asyncio.sleep(1)

    async def extract_text_content(self, driver):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            text_content = body.text
            return text_content.replace("\n", " ")
        except (NoSuchElementException, TimeoutException):
            return ""

    async def get_doi_content(self, doi_link):
        async with self.semaphore:
            try:
                driver = await self.get_driver()
                await self.navigate_to_doi_link(driver, doi_link)
                content = await self.extract_text_content(driver)
                await self.release_driver(driver)
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


# async def main():
#     scraper = DOIScraper(max_drivers=5)
#     doi_link = "10.1016/j.engappai.2024.107881"
#     content = await scraper.get_doi_content(doi_link)
#     print(content)


# asyncio.run(main())
