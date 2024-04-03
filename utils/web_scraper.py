import asyncio
import random
import aiohttp
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)


class WebScraper:
    def __init__(self, max_concurrent_tasks=120):
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def scrape_url(self, url, max_retries=3):
        options = uc.ChromeOptions()
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        retry_count = 0
        while retry_count < max_retries:
            try:
                driver = uc.Chrome(options=options)
                await self.update_user_agent(driver)
                await self.navigate_to_url(driver, url)
                content = await self.extract_text_content(driver)
                if any(
                    s in content
                    for s in [
                        "! There was a problem providing the content you requested Please contact us via our support center for more information and provide the details below.",
                        "The requested URL was rejected. Please consult with your administrator.",
                    ]
                ):
                    return ""
                print(f"Successfully scraped URL: {url}")
                return content
            except (aiohttp.ClientConnectorError, OSError) as e:
                print(f"Network error occurred while scraping URL: {url}")
                print(f"Error details: {str(e)}")
                retry_count += 1
                await asyncio.sleep(
                    random.uniform(1, 5)
                )  # Add a random delay between retries
            except Exception as e:
                print(f"Error occurred while scraping URL: {url}")
                print(f"Error details: {str(e)}")
                return ""
            finally:
                try:
                    driver.quit()
                except Exception:
                    pass

        print(f"Max retries exceeded for URL: {url}")
        return ""

    async def get_url_content(self, url):
        async with self.semaphore:
            return await self.scrape_url(url)

    async def update_user_agent(self, driver):
        ua = UserAgent()
        user_agent = ua.random
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": user_agent}
        )

    async def navigate_to_url(self, driver, url, retry=3):
        if not url.startswith("http"):
            url = f"https://doi.org/{url}"
        await self.update_user_agent(driver)
        try:
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                pass
            await asyncio.sleep(1)
        except WebDriverException as e:
            if retry > 0:
                print(f"Retrying URL: {url}")
                await self.navigate_to_url(driver, url, retry - 1)
            else:
                raise e

    async def extract_text_content(self, driver):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            text_content = body.text
            return text_content.replace("\n", " ")
        except (NoSuchElementException, TimeoutException):
            return ""
