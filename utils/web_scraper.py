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
import logging
from webdriver_manager.chrome import ChromeDriverManager

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

# Optional: Create a file handler to log messages to a file
file_handler = logging.FileHandler("webscraper.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class WebScraper:
    def __init__(self, max_concurrent_tasks=40, proxies_file="proxies.txt"):
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.url_queue = asyncio.Queue()
        self.proxies = self.load_proxies(proxies_file)
        self.user_agent = UserAgent()  # Initialize UserAgent object
        logger.info(
            f"WebScraper initialized with max_concurrent_tasks: {max_concurrent_tasks}"
        )

    def load_proxies(self, file_path):
        with open(file_path, "r") as file:
            proxies = file.read().splitlines()
            logger.info(f"Loaded {len(proxies)} proxies from file: {file_path}")
            return proxies

    async def scrape_url(self, max_retries=3, max_iterations=3):
        iteration_count = 0
        while True:
            if iteration_count >= max_iterations:
                logger.warning(
                    f"Worker task reached maximum iterations. Reinitializing..."
                )
                return

            try:
                url = await asyncio.wait_for(
                    self.url_queue.get(), timeout=60
                )  # Add a timeout for getting URLs from the queue
            except asyncio.TimeoutError:
                logger.warning("Timeout occurred while waiting for URLs in the queue.")
                continue

            options = uc.ChromeOptions()
            options.add_argument("--blink-settings=imagesEnabled=false")
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            proxy = random.choice(self.proxies)
            options.add_argument(f"--proxy-server={proxy}")

            retry_count = 0
            while retry_count < max_retries:
                try:
                    driver = uc.Chrome(options=options)
                    await self.update_user_agent(driver)
                    await asyncio.wait_for(
                        self.navigate_to_url(driver, url), timeout=30
                    )  # Add a timeout for navigation
                    content = await asyncio.wait_for(
                        self.extract_text_content(driver), timeout=30
                    )  # Add a timeout for content extraction
                    if any(
                        s in content
                        for s in [
                            "! There was a problem providing the content you requested Please contact us via our support center for more information and provide the details below.",
                            "The requested URL was rejected. Please consult with your administrator.",
                        ]
                    ):
                        self.url_queue.task_done()
                        logger.warning(
                            f"Failed to scrape URL because of bot protections: {url}"
                        )
                        return ""
                    logger.info(f"Successfully scraped URL: {url}")
                    self.url_queue.task_done()
                    return content
                except (aiohttp.ClientConnectorError, OSError) as e:
                    logger.error(f"Network error occurred while scraping URL: {url}")
                    logger.error(f"Error details: {str(e)}")
                    retry_count += 1
                    await asyncio.sleep(
                        random.uniform(1, 5)
                    )  # Add a random delay between retries
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout occurred while scraping URL: {url}")
                    retry_count += 1
                    await asyncio.sleep(
                        random.uniform(1, 5)
                    )  # Add a random delay between retries
                except Exception as e:
                    logger.error(f"Error occurred while scraping URL: {url}")
                    logger.error(f"Error details: {str(e)}")
                    self.url_queue.task_done()
                    return ""
                finally:
                    try:
                        driver.quit()
                    except Exception:
                        pass

            logger.warning(f"Max retries exceeded for URL: {url}")
            self.url_queue.task_done()
            iteration_count += 1
            return ""

    async def get_url_content(self, url):
        await self.url_queue.put(url)
        logger.info(f"URL added to queue: {url}")

    async def navigate_to_url(self, driver, url, retry=3):
        if not url.startswith("http"):
            url = f"https://doi.org/{url}"
        try:
            driver.get(url)
            logger.info(f"Navigating to URL: {url}")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                pass
            await asyncio.sleep(
                random.uniform(1, 3)
            )  # Add random delay to mimic human behavior
        except WebDriverException as e:
            if retry > 0:
                logger.warning(f"Retrying URL: {url}")
                await self.navigate_to_url(driver, url, retry - 1)
            else:
                raise e

    async def extract_text_content(self, driver):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            text_content = body.text
            logger.debug(f"Extracted text content from URL")
            return text_content.replace("\n", " ")
        except (NoSuchElementException, TimeoutException):
            logger.warning(f"Failed to extract text content from URL")
            return ""

    async def start_scraping(self):
        while True:
            async with self.semaphore:
                task = asyncio.create_task(self.scrape_url())
                logger.info(f"Started worker task: {task}")
                await task
