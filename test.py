import aiohttp
import asyncio
import json
import os
import sqlite3

api_key = "60261e8755ce5224a6dead5feec2e448"


async def fetch_scopus_abstracts(
    session, api_key, query, count=25, view="COMPLETE", response_format="json"
):
    """
    Fetches research abstracts from the Scopus API asynchronously.
    """
    base_url = "http://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": (
            "application/json" if response_format == "json" else "application/atom+xml"
        ),
    }

    params = {"query": query.replace("\\", ""), "count": count, "view": view}
    async with session.get(base_url, headers=headers, params=params) as response:
        return await response.json()


async def save_query_result(db_path, query_id, query_result):
    """
    Saves the query result text in the 'nodes' table.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE nodes SET query_result = ? WHERE node_id = ?",
        (json.dumps(query_result), query_id),
    )
    conn.commit()
    conn.close()


async def process_query(db_path, session, query_id, query):
    """
    Processes a single query asynchronously.
    """
    results = await fetch_scopus_abstracts(session, api_key, query)
    await save_query_result(db_path, query_id, results)
    print(f"Saved results for query with ID: {query_id}")


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
