import os
import asyncio
import aiofiles
import aiohttp
import sqlite3
import yaml
from bs4 import BeautifulSoup
import fitz  # PyMuPDF for PDF extraction
from llm_api_handler import LLM_APIHandler
from prompt_loader import get_prompt
from misc_utils import get_api_keys
import json
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 10  # Maximum number of retries in case of failure


class PaperCrawler:
    def __init__(self, root_dir, db_path, yaml_path):
        self.root_dir = root_dir
        self.db_path = db_path
        self.yaml_path = yaml_path
        self.conn = self.setup_database(db_path)
        self.api_keys = get_api_keys()
        self.api_handler = None
        self.load_categories_from_yaml()

    def setup_database(self, db_path):
        if not os.path.exists(db_path):
            open(db_path, "w").close()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                authors TEXT,
                doi TEXT,
                content TEXT,
                main_category INTEGER,
                sub_category INTEGER,
                reasoning TEXT,
                raw_output TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                parent_id INTEGER,
                description TEXT
            )
            """
        )
        conn.commit()
        return conn

    def load_categories_from_yaml(self):
        with open(self.yaml_path, "r") as file:
            categories = yaml.safe_load(file)["categories"]
        cursor = self.conn.cursor()
        for category in categories:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (id, name, description, parent_id) VALUES (?, ?, ?, ?)",
                (category["id"], category["name"], category["description"], None),
            )
            for subcategory in category.get("subcategories", []):
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (id, name, description, parent_id) VALUES (?, ?, ?, ?)",
                    (
                        subcategory["id"],
                        subcategory["name"],
                        subcategory["description"],
                        category["id"],
                    ),
                )
        self.conn.commit()

    async def extract_text_from_pdf(self, file_path):
        text = ""
        try:
            document = fitz.open(file_path)
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                text += page.get_text()
            logger.info(f"Successfully extracted text from PDF: {file_path}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
        return text

    async def extract_text_from_html(self, file_path):
        async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
            html_content = await file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator="\n")
        logger.info(f"Successfully extracted text from HTML: {file_path}")
        return text

    async def crawl_directory(self):
        tasks = []
        for subdir, _, files in os.walk(self.root_dir):
            for file in files:
                file_path = os.path.join(subdir, file)
                if file.lower().endswith(".pdf"):
                    tasks.append(self.extract_text_from_pdf(file_path))
                elif file.lower().endswith(".html") or file.lower().endswith(".htm"):
                    tasks.append(self.extract_text_from_html(file_path))
        return await asyncio.gather(*tasks)

    def get_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, parent_id, description FROM categories")
        categories = cursor.fetchall()
        category_dict = {
            cat[0]: {"name": cat[1], "parent_id": cat[2], "description": cat[3]}
            for cat in categories
        }
        return category_dict

    def get_next_sub_category_id(self, parent_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT MAX(id) FROM categories WHERE parent_id = ?", (parent_id,)
        )
        max_id = cursor.fetchone()[0]
        return (
            max_id + 1 if max_id else (parent_id * 100) + 1
        )  # Assuming sub-category ID starts from 101

    def add_new_sub_category(self, sub_category_name, parent_id, description):
        new_sub_category_id = self.get_next_sub_category_id(parent_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO categories (id, name, parent_id, description) VALUES (?, ?, ?, ?)",
            (new_sub_category_id, sub_category_name, parent_id, description),
        )
        self.conn.commit()
        return new_sub_category_id

    def insert_paper(
        self,
        title,
        authors,
        doi,
        content,
        main_category,
        sub_category,
        reasoning,
        raw_output,
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO papers (title, authors, doi, content, main_category, sub_category, reasoning, raw_output)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                authors,
                doi,
                content,
                main_category,
                sub_category,
                reasoning,
                raw_output,
            ),
        )
        self.conn.commit()

    async def query_llm(self, paper_content, categories):
        categories_json = json.dumps(categories) if categories else "{}"
        prompt = get_prompt(
            template_name="extract_zotero_content",
            NEW_PAPER=paper_content,
            CATEGORIES=categories_json,
        )
        response = await self.api_handler.generate_gemini_content(prompt)
        return response, prompt

    def parse_llm_response(self, response):
        try:
            if isinstance(response, list) and len(response) > 0:
                response_str = response[0]
            else:
                raise ValueError(
                    "Response is not in expected format (list with JSON string)."
                )

            json_matches = re.search(r"\{.*\}", response_str, re.DOTALL)
            if not json_matches:
                raise ValueError("No valid JSON object found in response")

            json_str = json_matches.group()
            response_data = json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None, None, None, None, None, None, None

        reasoning = response_data.get("reasoning", "")
        title = response_data.get("title", "")
        authors = response_data.get("authors", "")
        doi = response_data.get("doi", "")
        main_category_text = response_data.get("category", "")
        sub_category_text = response_data.get("sub_category", "")
        new_sub_category = response_data.get("new_sub_category", None)

        return (
            title,
            authors,
            doi,
            main_category_text,
            sub_category_text,
            reasoning,
            new_sub_category,
            response_str,
        )

    async def process_papers(self):
        self.api_handler = LLM_APIHandler(self.api_keys, aiohttp.ClientSession())
        texts = await self.crawl_directory()
        categories = self.get_categories()

        for text in texts:
            retries = 0
            success = False
            while retries < MAX_RETRIES and not success:
                try:
                    response, prompt = await self.query_llm(text, categories)
                    (
                        title,
                        authors,
                        doi,
                        main_category,
                        sub_category,
                        reasoning,
                        new_sub_category,
                        raw_output,
                    ) = self.parse_llm_response(response)

                    # Ensure main_category is a 1 or 2-digit integer
                    if not (main_category.isdigit() and 1 <= len(main_category) <= 2):
                        raise ValueError(
                            "Main category is not a valid 1 or 2-digit integer."
                        )

                    # Ensure sub_category is a 3-digit integer if provided
                    if sub_category and not (
                        sub_category.isdigit() and len(sub_category) == 3
                    ):
                        raise ValueError("Sub category is not a valid 3-digit integer.")

                    # Retry if sub_category is null and no new sub_category is proposed
                    if sub_category is None and new_sub_category is None:
                        raise ValueError(
                            "Sub category is null and no new sub-category proposed."
                        )

                    if title and authors and doi and main_category:
                        if new_sub_category:
                            main_category_id = int(main_category)
                            if main_category_id:
                                sub_category_id = self.add_new_sub_category(
                                    new_sub_category["name"],
                                    main_category_id,
                                    new_sub_category["description"],
                                )
                                sub_category = sub_category_id

                        self.insert_paper(
                            title,
                            authors,
                            doi,
                            text,
                            main_category,
                            sub_category,
                            reasoning,
                            raw_output,
                        )
                        success = True
                        print(f"Paper successfully classified: {title}")
                    else:
                        raise ValueError(
                            "Missing essential classification information."
                        )
                except Exception as e:
                    if retries == MAX_RETRIES - 1:
                        logger.error(
                            f"Failed to process text after {MAX_RETRIES} attempts: {text[:50]}..."
                        )
                        logger.error(f"Response: {response}")
                        logger.error(e)
                    retries += 1
                    retries += 1
                    logger.info(f"Retrying... Attempt {retries + 1}")

        await self.api_handler.session.close()

    def run(self):
        asyncio.run(self.process_papers())


if __name__ == "__main__":
    root_dir = r"C:\Users\bnsoh2\Zotero\storage"
    db_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Projects\Automated_Lit_Revs\classified_content\database.db"
    yaml_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Projects\Automated_Lit_Revs\classified_content\categories.yaml"
    crawler = PaperCrawler(root_dir, db_path, yaml_path)
    crawler.run()
