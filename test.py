import requests
import json
import os
import sqlite3

api_key = "60261e8755ce5224a6dead5feec2e448"


def clean_text(text):
    """
    Cleans and prepares text by replacing or removing certain characters.
    """
    replacements = {
        " ": "_",
        ".": "",
        "-": "_",
        ":": "",
        "/": "",
        "\\": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def fetch_scopus_abstracts(
    api_key, query, count=25, view="COMPLETE", response_format="json"
):
    """
    Fetches research abstracts from the Scopus API.
    """
    base_url = "http://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": (
            "application/json" if response_format == "json" else "application/atom+xml"
        ),
    }

    params = {"query": query.replace("\\", ""), "count": count, "view": view}
    response = requests.get(base_url, headers=headers, params=params)
    return response.json()


def save_query_result(cursor, query_id, query_result):
    """
    Saves the query result text in the 'nodes' table.
    """
    cursor.execute(
        "UPDATE nodes SET query_result = ? WHERE node_id = ?",
        (json.dumps(query_result), query_id),
    )


def process_queries(cursor):
    """
    Processes each query in the 'nodes' table.
    """
    cursor.execute("SELECT node_id, query FROM nodes WHERE node_type = 'query'")
    queries = cursor.fetchall()

    for query_id, query in queries:
        results = fetch_scopus_abstracts(api_key, query)
        save_query_result(cursor, query_id, results)
        print(f"Saved results for query with ID: {query_id}")


def process_database(db_path):
    """
    Processes an SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    process_queries(cursor)

    conn.commit()
    conn.close()


def process_searches_directory():
    """
    Processes the 'searches' directory and its subdirectories.
    """
    searches_path = os.path.join(os.getcwd(), "searches")
    for folder_name in os.listdir(searches_path):
        folder_path = os.path.join(searches_path, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.startswith("outline_") and file_name.endswith(".db"):
                    db_path = os.path.join(folder_path, file_name)
                    process_database(db_path)


# Start processing
process_searches_directory()
