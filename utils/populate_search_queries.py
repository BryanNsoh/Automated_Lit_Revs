import yaml
import asyncio
import re
import os
from pathlib import Path
import xmltodict
from utils.llm_api_handler import LLM_APIHandler
from utils.prompts import (
    get_prompt,
    outline,
    review_intention,
    scopus_search_guide,
    google_search_guide,
    section_intentions,
)


class QueryGenerator:
    def __init__(self, api_key_path):
        self.llm_api_handler = LLM_APIHandler(api_key_path)

    async def process_yaml(self, yaml_path, section_title, section_number):
        with open(yaml_path) as file:
            self.yaml_data = yaml.safe_load(file)

        # Determine the temporary output file path
        yaml_dir = Path(yaml_path).parent
        temp_output_file = yaml_dir / "temp_outline_queries.yaml"

        subsections = self.yaml_data["subsections"]
        for subsection in subsections:
            subsection_title = subsection["subsection_title"]
            print(f"Processing subsection: {subsection_title}")
            points = subsection["points"]
            for point in points:
                for point_key, point_data in point.items():
                    point_content = point_data["point_content"]

                    # Generate queries for each query type
                    query_types = [
                        key for key in point_data if key.endswith("_queries")
                    ]
                    for query_type in query_types:
                        queries = await self.get_queries(
                            section_title,
                            subsection_title,
                            point_content,
                            eval(query_type.replace("_queries", "_search_guide")),
                            section_number,
                        )
                        print(f"{query_type}: ", queries)
                        point_data[query_type] = queries

                        # Create empty responses for each query
                        for i, query in enumerate(queries):
                            query_id = f"{query_type}_{i}"
                            query_data = {
                                "query_id": query_id,
                                "query": query,
                                "responses": [
                                    {
                                        "response_id": f"{query_id}_response_{j}",
                                        "title": "",
                                        "DOI": "",
                                        "full_text": "",
                                        "inline_citation": "",
                                        "full_citation": "",
                                        "publication_year": "",
                                        "authors": [],
                                        "citation_count": 0,
                                        "pdf_link": "",
                                        "journal": "",
                                        "analysis": "",
                                        "verbatim_quote1": "",
                                        "verbatim_quote2": "",
                                        "verbatim_quote3": "",
                                        "relevance_score1": 0,
                                        "relevance_score2": 0,
                                        "limitations": "",
                                        "inline_citation": "",
                                        "full_citation": "",
                                    }
                                    for j in range(5)
                                ],
                            }
                            point_data[query_type][i] = query_data

                    # Write the updated yaml_data to the temporary output file
                    with open(temp_output_file, "w") as file:
                        yaml.dump(self.yaml_data, file)

        # Rename the temporary output file to the final output file
        output_file = yaml_dir / "outline_queries.yaml"
        os.rename(temp_output_file, output_file)

    async def get_queries(
        self,
        section_title,
        subsection_title,
        point_content,
        search_guidance,
        section_number,
    ):
        prompt = get_prompt(
            template_name="generate_queries",
            review_intention=review_intention,
            section_intention=section_intentions[str(section_number)],
            point_content=point_content,
            section_title=section_title,
            subsection_title=subsection_title,
            search_guidance=search_guidance,
        )
        response = await self.llm_api_handler.generate_gemini_content(prompt)
        queries = self.parse_response(response)
        print(queries)
        return queries

    def parse_response(self, response):
        try:
            data = xmltodict.parse(response)
            queries = None

            # Find the first key ending with "_queries"
            for key in data:
                if key.endswith("_queries"):
                    queries = data[key]
                    break

            if queries:
                print(f"Parsed {key}.")
                return queries["query"]
            else:
                print("No queries found in the response.")
                return []
        except xmltodict.expat.ExpatError as exc:
            print(f"Error parsing XML response: {exc}")
            return []


# Example usage
# yaml_path = "input.yaml"
# section_title = "Introduction"
# section_number = 1
# api_key_path = "path/to/api/key"
# processor = QueryGenerator(api_key_path)
# asyncio.run(processor.process_yaml(yaml_path, section_title, section_number))
