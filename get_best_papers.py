import google.generativeai as genai
import json
import logging
import sqlite3
import os
import re
import asyncio
import aiohttp
import time
from prompts import return_best_results

# Logger setup
logging.basicConfig(level=logging.INFO)


class LLM_APIHandler:
    def __init__(self, key_path):
        self.load_api_keys(key_path)
        self.semaphore = asyncio.Semaphore(1)  # Limit to 1 request at a time
        self.last_request_time = 0
        genai.configure(api_key=self.gemini_api_key)

    def load_api_keys(self, key_path):
        with open(key_path, "r") as file:
            api_keys = json.load(file)
            self.gemini_api_key = api_keys["GEMINI_API_KEY"]

    async def generate_gemini_content(self, prompt):
        async with self.semaphore:
            current_time = time.time()
            elapsed_time = current_time - self.last_request_time
            if elapsed_time < 1:
                await asyncio.sleep(1 - elapsed_time)
            try:
                async with aiohttp.ClientSession() as session:
                    model = genai.GenerativeModel("gemini-pro")
                    response = await model.generate_content_async(prompt)
                    print(response.text)
                    self.last_request_time = time.time()
                    return self.extract_json(response.text)
            except Exception as e:
                logging.error(f"Error in Gemini API call: {e}")
                raise

    def extract_json(self, response):
        try:
            json_start = response.index("[")
            json_end = response.rindex("]") + 1
            json_string = response[json_start:json_end]
            return json.loads(json_string)
        except (ValueError, json.JSONDecodeError):
            raise ValueError("Invalid JSON format in the response")


async def process_query_node(node_id, query_result, text, llm_handler, cursor):
    if query_result not in ["null", "[]"]:
        # Retrieve the outline and review_intention from the database (assuming they are stored in separate tables)
        cursor.execute(
            "SELECT title FROM nodes WHERE node_id = (SELECT parent_id FROM nodes WHERE node_id = ?)",
            (node_id,),
        )
        outline = cursor.fetchone()[0]
        cursor.execute(
            "SELECT title FROM nodes WHERE node_id = (SELECT parent_id FROM nodes WHERE node_id = (SELECT parent_id FROM nodes WHERE node_id = ?))",
            (node_id,),
        )
        review_intention = cursor.fetchone()[0]

        prompt = return_best_results(outline, review_intention, text, query_result)
        try:
            json_response = await llm_handler.generate_gemini_content(prompt)
            for result in json_response:
                doi = result["doi"]
                title = result["title"]
                cursor.execute(
                    """
                    INSERT INTO query_results (query_id, doi, title)
                    VALUES (?, ?, ?)
                """,
                    (node_id, doi, title),
                )
        except ValueError as e:
            logging.error(
                f"Error processing query result for node ID: {node_id}. Error: {str(e)}"
            )


async def process_json_files(folder_path, llm_handler):
    db_file = None
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".db"):
            db_file = os.path.join(folder_path, file_name)
            break

    if db_file is None:
        logging.info(f"No database file found in folder: {folder_path}")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT node_id, query_result, text FROM nodes WHERE node_type = 'query'"
    )
    query_nodes = cursor.fetchall()

    tasks = []
    for node_id, query_result, text in query_nodes:
        if query_result not in ["null", "[]"]:
            task = asyncio.create_task(
                process_query_node(node_id, query_result, text, llm_handler, cursor)
            )
            tasks.append(task)

    await asyncio.gather(*tasks)

    conn.commit()
    conn.close()


async def main():
    key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    llm_handler = LLM_APIHandler(key_path)

    searches_folder = "searches"
    if not os.path.exists(searches_folder):
        logging.info(f"The 'searches' folder does not exist.")
        return

    tasks = []
    for folder_name in os.listdir(searches_folder):
        if re.match(r"sec\d+_results", folder_name):
            folder_path = os.path.join(searches_folder, folder_name)
            task = asyncio.create_task(process_json_files(folder_path, llm_handler))
            tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
