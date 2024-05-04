import asyncio
import logging
import json
from llm_api_handler import LLM_APIHandler
from prompts import get_prompt
import aiohttp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
file_handler = logging.FileHandler("paper_ranker.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class PaperRanker:
    def __init__(self, api_key_path, session, max_retries=4):
        self.llm_api_handler = LLM_APIHandler(api_key_path, session)
        self.max_retries = max_retries

    async def process_query(self, query_key, query_data, point_context):
        retry_count = 0
        while retry_count < self.max_retries:
            prompt = get_prompt(
                template_name="rank_papers",
                full_text=query_data,
                point_context=point_context,
            )
            try:
                print(f"Processing queries for {point_context}...")
                response = await self.llm_api_handler.generate_cohere_content(prompt)
                if response is None:
                    logger.warning(
                        "Received None response from the Gemini API. Skipping query."
                    )
                    return None
                try:
                    # Find text between the first and last curly braces
                    response = response[response.find("{") : response.rfind("}") + 1]
                    json_data = json.loads(response)
                    json_data["DOI"] = query_data["DOI"]
                    json_data["title"] = query_data["title"]
                    logger.debug(f"Successfully processed query.")
                    print(f"Contents: {json_data}")
                    return json_data
                except json.JSONDecodeError:
                    logger.warning(
                        f"Invalid JSON response for the current query. Retrying immediately..."
                    )
                    retry_count += 1
            except Exception as e:
                logger.exception(f"Error processing query: {str(e)}")
                retry_count += 1

        logger.error(f"Max retries reached for current query. Skipping query.")
        return None

    async def process_queries(self, input_json, point_context):
        tasks = []
        for query_key, query_data in input_json.items():
            if not query_data.get("DOI") or not query_data.get("title"):
                logger.warning(
                    f"Discarding query {query_key} due to missing DOI or title."
                )
                continue
            task = asyncio.create_task(
                self.process_query(query_key, query_data, point_context)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        output_json = {}
        for query_key, result in zip(input_json.keys(), results):
            if result and isinstance(result, dict):
                relevance_score = result.get("relevance_score")
                try:
                    relevance_score = float(relevance_score)
                    if relevance_score > 0.5:
                        output_json[query_key] = result
                except (ValueError, TypeError):
                    logger.warning(
                        f"Invalid relevance score for query {query_key}. Skipping paper."
                    )

        return output_json


async def main(input_json, point_context):
    api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"

    async with aiohttp.ClientSession() as session:
        ranker = PaperRanker(api_key_path, session)
        logger.info("Starting paper ranking process...")
        output_json = await ranker.process_queries(input_json, point_context)
        logger.info("Paper ranking process completed.")
        return output_json


if __name__ == "__main__":
    input_json = {
        "query_1": {
            "DOI": "https://doi.org/10.1007/bf00281114",
            "authors": ["Jarrett Rj"],
            "citation_count": 156,
            "journal": "Diabetologia",
            "pdf_link": "https://link.springer.com/content/pdf/10.1007%2FBF00281114.pdf",
            "publication_year": 1984,
            "title": "Type 2 (non-insulin-dependent) diabetes mellitus and coronary heart disease ? chicken, egg or neither?",
            "full_text": "This is the full text of the paper...",
        },
        "query_2": {
            "DOI": "https://doi.org/10.1001/jamainternmed.2019.6969",
            "authors": [
                "Victor W. Zhong",
                "Linda Van Horn",
                "Philip Greenland",
                "Mercedes R. Carnethon",
                "Hongyan Ning",
                "John T. Wilkins",
                "Donald M. Lloyd‐Jones",
                "Norrina B. Allen",
            ],
            "citation_count": 221,
            "journal": "JAMA internal medicine",
            "pdf_link": "https://jamanetwork.com/journals/jamainternalmedicine/articlepdf/2759737/jamainternal_zhong_2020_oi_190112.pdf",
            "publication_year": 2020,
            "title": "Associations of Processed Meat, Unprocessed Red Meat, Poultry, or Fish Intake With Incident Cardiovascular Disease and All-Cause Mortality",
            "full_text": "This is the full text of the paper...",
        },
        "query_3": {
            "DOI": "https://doi.org/10.1016/s0034-5288(18)33737-8",
            "authors": ["S.F. Cueva", "H. Sillau", "Abel Valenzuela", "H. P. Ploog"],
            "citation_count": 181,
            "journal": "Research in Veterinary Science/Research in veterinary science",
            "publication_year": 1974,
            "title": "High Altitude Induced Pulmonary Hypertension and Right Heart Failure in Broiler Chickens",
            "full_text": "This is the full text of the paper...",
        },
        "query_4": {
            "DOI": "https://doi.org/10.2307/1588087",
            "authors": ["Sherwin A. Hall", "Nicanor Machicao"],
            "citation_count": 58,
            "journal": "Avian diseases",
            "publication_year": 1968,
            "title": "Myocarditis in Broiler Chickens Reared at High Altitude",
            "full_text": "This is the full text of the paper...",
        },
        "query_5": {
            "DOI": "https://doi.org/10.1038/srep14727",
            "authors": [
                "Huaguang Lu",
                "Yi Tang",
                "Patricia A. Dunn",
                "Eva Wallner-Pendleton",
                "Lin Lin",
                "Eric A. Knoll",
            ],
            "citation_count": 82,
            "journal": "Scientific reports",
            "pdf_link": "https://www.nature.com/articles/srep14727.pdf",
            "publication_year": 2015,
            "title": "Isolation and molecular characterization of newly emerging avian reovirus variants and novel strains in Pennsylvania, USA, 2011–2014",
            "full_text": "This is the full text of the paper...",
        },
    }
    point_context = "Heart disease in chickens."

    output_json = asyncio.run(main(input_json, point_context))
    print(json.dumps(output_json, indent=2))
