import aiosqlite
import re
import asyncio
import aiohttp
import aiofiles
from web_scraper import WebScraper  # Ensure this module is available
import logging
import sys
import os

# Configurable global variables
FORBIDDEN_TEXT = "You are accessing a machine-readable page."
WORD_COUNT_THRESHOLD = 2000


# Function to extract entries from .bib content and clean fields
def extract_entries(bib_content):
    entries = bib_content.split("@")[1:]  # Splitting entries
    extracted_entries = []

    for entry in entries:
        entry_dict = {
            "title": None,
            "year": None,
            "doi": None,
            "url": None,
            "author": None,
        }
        entry_lines = entry.split("\n")

        for line in entry_lines:
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("{}").strip(",")
                if key in entry_dict:
                    entry_dict[key] = value

        # Clean the fields
        for key in entry_dict:
            if entry_dict[key]:
                entry_dict[key] = entry_dict[key].rstrip(".}").strip()

        extracted_entries.append(entry_dict)

    return extracted_entries


# Async function to read the .bib file content
async def read_bib_file(file_path):
    async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
        return await file.read()


# Async function to initialize the database
async def init_db(db_path):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                title TEXT,
                year TEXT,
                doi TEXT,
                url TEXT,
                author TEXT,
                content TEXT
            )
            """
        )
        await db.commit()


# Async function to load entries from .bib file to database
async def load_entries_to_db(entries, db_path):
    async with aiosqlite.connect(db_path) as db:
        for entry in entries:
            await db.execute(
                """
                INSERT INTO entries (title, year, doi, url, author, content)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["title"],
                    entry["year"],
                    entry["doi"],
                    entry["url"],
                    entry["author"],
                    None,  # Initialize content as None
                ),
            )
        await db.commit()


# Function to scrape content and update the database
async def scrape_and_update(db_path):
    success_count = 0
    failure_count = 0
    total_count = 0
    async with aiohttp.ClientSession() as session:
        scraper = WebScraper(session=session)
        try:
            await scraper.initialize()
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            return  # Early return if initialization fails

        scrape_tasks = []

        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT title, year, doi, url, author, content FROM entries"
            ) as cursor:
                async for row in cursor:
                    entry = {
                        "title": row[0],
                        "year": row[1],
                        "doi": row[2],
                        "url": row[3],
                        "author": row[4],
                        "content": row[5],
                    }
                    reason = None

                    if entry["content"] is None:
                        reason = "Content is NULL"
                    elif FORBIDDEN_TEXT in entry["content"]:
                        reason = "Contains forbidden text"
                    elif len(entry["content"].split()) < WORD_COUNT_THRESHOLD:
                        reason = "Content is shorter than 2000 words"

                    if reason:
                        total_count += 1
                        print(f"Title: {entry['title']}\nReason: {reason}\n")
                        doi = entry.get("doi")
                        url = entry.get("url")

                        # Convert DOI to URL if DOI is present
                        target_url = (
                            f"https://doi.org/{doi}"
                            if doi and not doi.startswith("http")
                            else (doi if doi else url)
                        )
                        if target_url:
                            scrape_task = asyncio.create_task(
                                scraper.get_url_content(target_url)
                            )
                            scrape_tasks.append((entry, scrape_task, reason))

            for entry, scrape_task, reason in scrape_tasks:
                content = await scrape_task
                content_success = False

                # Check if content satisfies the criteria after scraping
                if content:
                    if reason == "Content is NULL" and content:
                        content_success = True
                    elif (
                        reason == "Contains forbidden text"
                        and FORBIDDEN_TEXT not in content
                    ):
                        content_success = True
                    elif (
                        reason == "Content is shorter than 2000 words"
                        and len(content.split()) >= WORD_COUNT_THRESHOLD
                    ):
                        content_success = True

                if content_success:
                    await db.execute(
                        """
                        UPDATE entries
                        SET content = ?
                        WHERE title = ? AND year = ? AND doi = ? AND url = ? AND author = ?
                        """,
                        (
                            content,
                            entry["title"],
                            entry["year"],
                            entry["doi"],
                            entry["url"],
                            entry["author"],
                        ),
                    )
                    success_count += 1
                else:
                    failure_count += 1

            await db.commit()

        await scraper.close()

        # Printing the first 1000 words of the content for each updated entry
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT title, content FROM entries WHERE content IS NOT NULL"
            ) as cursor:
                async for row in cursor:
                    title = row[0]
                    content = row[1]
                    first_1000_words = " ".join(content.split()[:1000])
                    print(
                        f"Title: {title}\nContent Preview:\n{first_1000_words}\n{'-'*80}\n"
                    )

    # Print the summary of the scraping process
    print(f"Total entries checked: {total_count}")
    print(f"Successful updates: {success_count}")
    print(f"Failed updates: {failure_count}")


# Main async function to run the whole process
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

    db_path = "classified_content/bib_entries.db"
    bib_file_path = "classified_content/citations.bib"

    # Check if the database exists
    db_exists = os.path.exists(db_path)

    if not db_exists:
        # Read the .bib file content
        bib_content = await read_bib_file(bib_file_path)
        entries = extract_entries(bib_content)

        # Initialize the database and load entries
        await init_db(db_path)
        await load_entries_to_db(entries, db_path)

    # Scrape content and update the database
    await scrape_and_update(db_path)

    print(
        "Entries have been successfully extracted, scraped, and stored in the SQLite database."
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
    finally:
        # Ensure all asyncio resources are properly closed
        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
