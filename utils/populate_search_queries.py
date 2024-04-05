import yaml
import asyncio
import aiofiles
import re
import os
from pathlib import Path
import json
from llm_api_handler import LLM_APIHandler
from prompts import (
    get_prompt,
    review_intention,
    scopus_search_guide,
    alex_search_guide,
    section_intentions,
)


class QueryGenerator:
    def __init__(self, api_key_path, max_retries=10):
        self.llm_api_handler = LLM_APIHandler(api_key_path)
        self.max_retries = max_retries

    async def process_yaml(self, yaml_path, section_title, section_number):
        async with aiofiles.open(yaml_path) as file:
            self.yaml_data = yaml.safe_load(await file.read())

        # Determine the temporary output file path
        yaml_dir = Path(yaml_path).parent
        temp_output_file = yaml_dir / "temp_outline_queries.yaml"

        subsections = self.yaml_data["subsections"]
        tasks = []
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
                        task = asyncio.create_task(
                            self.process_query_type(
                                section_title,
                                subsection_title,
                                point_content,
                                eval(query_type.replace("_queries", "_search_guide")),
                                section_number,
                                query_type,
                                point_data,
                            )
                        )
                        tasks.append(task)

        await asyncio.gather(*tasks)

        # Write the updated yaml_data to the temporary output file
        async with aiofiles.open(temp_output_file, "w") as file:
            await file.write(yaml.dump(self.yaml_data))

        # Rename the temporary output file to the final output file
        output_file = yaml_dir / "outline_queries.yaml"
        os.rename(temp_output_file, output_file)

    async def process_query_type(
        self,
        section_title,
        subsection_title,
        point_content,
        search_guidance,
        section_number,
        query_type,
        point_data,
    ):
        queries = await self.get_queries(
            section_title,
            subsection_title,
            point_content,
            search_guidance,
            section_number,
        )
        print(f"{query_type}: ", queries)
        point_data[query_type] = queries

        # Create 1 empty response for each query
        for i, query in enumerate(queries):
            query_id = f"{query_type}_{i}"
            query_data = {
                "query_id": query_id,
                "query": query,
                "responses": [
                    {
                        "response_id": f"{query_id}_response_{j}",
                    }
                    for j in range(1)
                ],
            }
            point_data[query_type][i] = query_data

    async def get_queries(
        self,
        section_title,
        subsection_title,
        point_content,
        search_guidance,
        section_number,
    ):
        retry_count = 0
        while retry_count < self.max_retries:
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
            if queries:
                print(queries)
                return queries
            retry_count += 1
            print(f"Retrying... Attempt {retry_count}")
        print("Max retries reached. Returning empty queries.")
        return []

    def parse_response(self, response):
        try:
            data = json.loads(response)
            queries = None

            # Find the key ending with "_queries"
            for key in data:
                if key.endswith("_queries"):
                    queries = data[key]
                    break

            if queries:
                print(f"Parsed {key}.")
                return queries
            else:
                print("No queries found in the response.")
                return []
        except json.JSONDecodeError as exc:
            print(f"Error parsing JSON response: {exc}")
            return None


# Example usage
section_info = {
    4: "AUTOMATED DATA PROCESSING IN THE CLOUD: Examines the importance of data quality and preprocessing in the cloud, containerization strategies for scalable and autonomous deployment, and the deployment of machine learning (ML) models for real-time data processing and inference.",
    5: "GENERATING AND APPLYING IRRIGATION INSIGHTS: Focuses on the application of ML-generated insights to control irrigation systems without manual intervention, investigating the real-time generation and automated application of actionable irrigation insights, and the importance of interpretability and explainability in ML models.",
    6: "INTEGRATION, INTEROPERABILITY, AND STANDARDIZATION: Explores the challenges and strategies for integrating automated systems with existing irrigation infrastructure and other precision agriculture technologies, highlighting the importance of interoperability and standardization in enabling seamless communication and compatibility.",
    7: "MONITORING AND ENSURING SYSTEM RELIABILITY: Focuses on strategies for ensuring the robustness and reliability of the automated irrigation system, including resilience and fault tolerance, advanced monitoring techniques, closed-loop control, and addressing security concerns and risks in large-scale deployments.",
    8: "CASE STUDIES AND REAL-WORLD IMPLEMENTATIONS: Presents detailed examples of successful deployments of end-to-end automated irrigation systems in various agricultural settings, highlighting lessons learned, challenges encountered, and best practices derived from real-world implementations.",
}

api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
processor = QueryGenerator(api_key_path)

for section_number, section_title in section_info.items():
    yaml_path = rf"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section{section_number}\research_paper_outline.yaml"
    asyncio.run(processor.process_yaml(yaml_path, section_title, section_number))

# section_title = "DATA COLLECTION TO CLOUD: AUTOMATION AND REAL-TIME PROCESSING"
# section_number = 3
# api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
# processor = QueryGenerator(api_key_path)
# asyncio.run(processor.process_yaml(yaml_path, section_title, section_number))
