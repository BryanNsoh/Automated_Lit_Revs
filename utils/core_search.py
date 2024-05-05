import aiohttp
import asyncio
import json
import logging

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

# Create a file handler to log messages to a file
file_handler = logging.FileHandler("core_search.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class CORESearch:
    def __init__(self, key_path, max_results):
        self.load_api_keys(key_path)
        self.base_url = "https://api.core.ac.uk/v3"
        self.max_results = max_results

    def load_api_keys(self, key_path):
        try:
            with open(key_path, "r") as file:
                api_keys = json.load(file)
            self.core_api_key = api_keys["CORE_API_KEY"]
            logger.info("API keys loaded successfully.")
        except FileNotFoundError:
            logger.error(f"API key file not found at path: {key_path}")
        except KeyError:
            logger.error("CORE_API_KEY not found in the API key file.")
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in the API key file.")

    async def search(self, search_query):
        headers = {
            "Authorization": f"Bearer {self.core_api_key}",
            "Accept": "application/json",
        }

        params = {
            "q": search_query,
            "limit": self.max_results,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/search/works", headers=headers, json=params
            ) as response:
                if response.status == 200:
                    logger.info("CORE API request successful.")
                    response_json = await response.json()
                    return response_json
                else:
                    logger.warning(
                        f"CORE API request failed with status code: {response.status}"
                    )
                    return None

    async def search_and_parse(self, query):
        try:
            search_query = query["search_query"]
            response = await self.search(search_query)

            if response is None:
                logger.warning(f"Empty API response for query: {search_query}")
                return {}

            results = response.get("results", [])
            parsed_result = {}

            if results:
                print(results)
                entry = results[0]
                parsed_result = {
                    "DOI": entry.get("doi", ""),
                    "authors": [author["name"] for author in entry.get("authors", [])],
                    "citation_count": entry.get("citationCount", 0),
                    "journal": entry.get("publisher", ""),
                    "pdf_link": entry.get("downloadUrl", ""),
                    "publication_year": entry.get("publicationYear"),
                    "title": entry.get("title", ""),
                    "full_text": entry.get("fullText", ""),
                    "query_rationale": query["query_rationale"],
                }

            return parsed_result
        except Exception as e:
            logger.error(
                f"An error occurred while searching and parsing results for query: {search_query}. Error: {e}"
            )
            return {}

    async def search_and_parse_json(self, input_json):
        try:
            updated_json = {}
            for query_id, query in input_json.items():
                parsed_result = await self.search_and_parse(query)
                updated_json[query_id] = parsed_result
            return updated_json
        except Exception as e:
            logger.error(
                f"An error occurred while processing the input JSON. Error: {e}"
            )
            return {}


async def main():
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
    max_results = 1

    core_search = CORESearch(api_key_path, max_results)

    input_json = {
        "query_1": {
            "search_query": "climate change, water resources",
            "query_rationale": "This query is essential to understand the overall impact of climate change on global water resources, providing a broad understanding of the topic.",
        },
        "query_2": {
            "search_query": "water scarcity, (hydrologist OR water expert)",
            "query_rationale": "This query is necessary to identify areas with high water scarcity and how climate change affects the global distribution of water resources.",
        },
        "query_3": {
            "search_query": "sea level rise, coastal erosion",
            "query_rationale": "This query is crucial to understand the impact of climate change on coastal regions and the resulting effects on global water resources.",
        },
        "query_4": {
            "search_query": "water conservation, climate change mitigation, environmental studies",
            "query_rationale": "This query is important to identify strategies for water conservation and their role in mitigating the effects of climate change on global water resources.",
        },
        "query_5": {
            "search_query": "glacier melting, cryosphere",
            "query_rationale": "This query is necessary to understand the impact of climate change on glaciers and the resulting effects on global water resources.",
        },
    }

    updated_json = await core_search.search_and_parse_json(input_json)

    # Remove the "full_text" key from each query result
    for query_result in updated_json.values():
        query_result.pop("full_text", None)

    print(json.dumps(updated_json, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
