import aiohttp
import asyncio
import json
import os
import sqlite3
import time
from collections import deque

api_key = "60261e8755ce5224a6dead5feec2e448"

# Initialize a deque to track the timestamps of the last N requests, where N is the rate limit
request_times = deque(maxlen=6)


async def fetch_scopus_abstracts(
    session, api_key, query, count=25, view="COMPLETE", response_format="json"
):
    """
    Fetches research abstracts from the Scopus API asynchronously, ensuring compliance with rate limits.
    """
    base_url = "http://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": (
            "application/json" if response_format == "json" else "application/atom+xml"
        ),
    }

    params = {"query": query.replace("\\", ""), "count": count, "view": view}

    # Ensure we comply with the rate limit
    while True:
        current_time = time.time()
        if not request_times or current_time - request_times[0] >= 1:
            request_times.append(current_time)
            break
        else:
            await asyncio.sleep(
                0.1
            )  # Sleep briefly to wait for the rate limit window to pass

    async with session.get(base_url, headers=headers, params=params) as response:
        return await response.json()


async def save_query_result(db_path, query_id, filtered_results):
    """Saves the filtered query results in the 'nodes' table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE nodes SET query_result = ? WHERE node_id = ?",
        (json.dumps(filtered_results), query_id),
    )
    conn.commit()
    conn.close()


async def process_query(db_path, session, query_id, query):
    """Processes a single query asynchronously, ensuring compliance with rate limits."""
    try:
        results = await fetch_scopus_abstracts(session, api_key, query)

        if (
            results is None
            or "search-results" not in results
            or "entry" not in results["search-results"]
        ):
            filtered_results = None
        else:
            filtered_results = []
            for entry in results["search-results"]["entry"]:
                title = entry.get("dc:title")
                doi = entry.get("prism:doi")
                description = entry.get("dc:description")
                journal = entry.get("prism:publicationName")
                citation_count = entry.get("citedby-count", "0")
                authors = [
                    author.get("authname")
                    for author in entry.get("author", [])
                    if author.get("authname") is not None
                ]

                if title is None:
                    print(f"Skipping entry with doi: {doi} due to missing title")
                    continue
                else:
                    filtered_results.append(
                        {
                            "title": title,
                            "doi": doi,
                            "description": description,
                            "journal": journal,
                            "authors": authors,
                            "citation_count": citation_count,
                        }
                    )

        await save_query_result(db_path, query_id, filtered_results)
        print(f"Saved filtered results for query with ID: {query_id}")
    except Exception as e:
        print(f"Error processing query with ID: {query_id}. Error: {str(e)}")
        await save_query_result(db_path, query_id, None)


async def process_database(db_path):
    """
    Processes an SQLite database file asynchronously.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT node_id, query FROM nodes WHERE node_type = 'query'")
    queries = cursor.fetchall()
    conn.close()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for query_id, query in queries:
            task = asyncio.ensure_future(
                process_query(db_path, session, query_id, query)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)


async def process_searches_directory():
    """
    Processes the 'searches' directory and its subdirectories asynchronously.
    """
    searches_path = os.path.join(os.getcwd(), "searches")
    for folder_name in os.listdir(searches_path):
        folder_path = os.path.join(searches_path, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.startswith("outline_") and file_name.endswith(".db"):
                    db_path = os.path.join(folder_path, file_name)
                    await process_database(db_path)


# Start processing asynchronously
asyncio.run(process_searches_directory())
