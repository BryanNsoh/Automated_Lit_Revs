from misc_utils import get_api_keys
import asyncio
import logging
import re
from llm_api_handler import LLM_APIHandler
from prompts import get_prompt
import aiohttp
import json

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
    def __init__(self, session, max_retries=4):
        self.api_keys = get_api_keys()
        self.llm_api_handler = LLM_APIHandler(self.api_keys, session)
        self.max_retries = max_retries

    async def process_query(self, query_key, query_data, point_context):
        retry_count = 0
        while retry_count < self.max_retries:
            prompt = get_prompt(
                template_name="rank_papers",
                full_text=query_data.get("full_text", ""),
                point_context=point_context,
                query_rationale=query_data.get("query_rationale", ""),
            )
            try:
                print(f"Processing queries for {point_context}...")
                response = await self.llm_api_handler.generate_cohere_content(prompt)
                print(f"Response: {response}")
                if response is None:
                    logger.warning(
                        "Received None response from the Gemini API. Skipping query."
                    )
                    return None

                try:
                    # Extract the relevance score using the specified token format
                    relevance_score_match = re.search(
                        r"<<relevance>>(\d+\.\d+)<<relevance>>",
                        response,
                    )

                    if relevance_score_match:
                        relevance_score_str = relevance_score_match.group(1)
                        try:
                            relevance_score = float(relevance_score_str)
                            if relevance_score > 0.5:
                                logger.debug(f"Successfully processed query.")
                                return {
                                    "DOI": query_data.get("DOI", ""),
                                    "title": query_data.get("title", ""),
                                    "analysis": response,
                                    "relevance_score": relevance_score,
                                }
                            else:
                                logger.debug(
                                    f"Relevance score {relevance_score} is below the threshold. Skipping query."
                                )
                                return None
                        except ValueError:
                            logger.warning(
                                f"Extracted relevance score '{relevance_score_str}' is not a valid float. Retrying..."
                            )
                            retry_count += 1
                    else:
                        logger.warning(
                            f"No relevance score found between <|relevance|> tokens in the response for query {query_key}. Response: {response}"
                        )
                        retry_count += 1
                except Exception as e:
                    logger.warning(
                        f"Error extracting relevance score for query {query_key}: {str(e)}. Retrying..."
                    )
                    retry_count += 1
            except Exception as e:
                logger.exception(f"Error processing query {query_key}: {str(e)}")
                retry_count += 1

        logger.error(f"Max retries reached for query {query_key}. Skipping query.")
        return None

    async def process_queries(self, input_json, point_context):
        tasks = []
        for query_key, query_data in input_json.items():
            task = asyncio.create_task(
                self.process_query(query_key, query_data, point_context)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        output_json = {}
        for query_key, result in zip(input_json.keys(), results):
            if result and isinstance(result, dict):
                output_json[query_key] = result

        return output_json


async def main(input_json, point_context):
    async with aiohttp.ClientSession() as session:
        ranker = PaperRanker(session)
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
            "query_rationale": "This query aims to understand the relationship between Type 2 diabetes and coronary heart disease in chickens.",
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
            "query_rationale": "This query investigates the associations between different types of meat intake, including poultry, and cardiovascular disease and mortality.",
        },
        "query_3": {
            "DOI": "https://doi.org/10.1016/s0034-5288(18)33737-8",
            "authors": ["S.F. Cueva", "H. Sillau", "Abel Valenzuela", "H. P. Ploog"],
            "citation_count": 181,
            "journal": "Research in Veterinary Science/Research in veterinary science",
            "publication_year": 1974,
            "title": "High Altitude Induced Pulmonary Hypertension and Right Heart Failure in Broiler Chickens",
            "full_text": "This is the full text of the paper...",
            "query_rationale": "This query focuses on the effects of high altitude on pulmonary hypertension and right heart failure specifically in broiler chickens.",
        },
        "query_4": {
            "DOI": "https://doi.org/10.2307/1588087",
            "authors": ["Sherwin A. Hall", "Nicanor Machicao"],
            "citation_count": 58,
            "journal": "Avian diseases",
            "publication_year": 1968,
            "title": "Myocarditis in Broiler Chickens Reared at High Altitude",
            "full_text": "This is the full text of the paper...",
            "query_rationale": "This query examines myocarditis in broiler chickens reared at high altitude, providing insight into heart disease in this specific context.",
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
            "query_rationale": "This query looks at the isolation and characterization of new avian reovirus variants and strains, which may have implications for chicken health.",
        },
    }
    point_context = "Heart disease in chickens."

    output_json = asyncio.run(main(input_json, point_context))
    print(json.dumps(output_json, indent=2))
