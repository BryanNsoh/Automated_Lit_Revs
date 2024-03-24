"""
research_paper_outline_generator.py

This module provides a class to generate a YAML-formatted research paper outline from a JSON input file.
"""

import json
import os
import yaml


class ResearchPaperOutlineGenerator:
    def __init__(self, json_file, output_directory):
        with open(json_file) as file:
            self.data = json.load(file)
        self.output_directory = output_directory

    def generate_outline(self):
        outline_data = []
        for i, subsection in enumerate(self.data["subsections"], start=1):
            subsection_data = {
                "index": i,
                "subsection_title": subsection["subsection_title"],
                "points": [],
            }
            for j, point in enumerate(subsection["points"], start=1):
                point_data = {
                    f"Point {j}": {
                        "point_content": point["point_content"],
                        "scopus_queries": self.generate_queries(
                            point["scopus_queries"]
                        ),
                        "google_queries": self.generate_queries(
                            point["google_queries"]
                        ),
                    }
                }
                subsection_data["points"].append(point_data)
            outline_data.append(subsection_data)

        output_file = os.path.join(self.output_directory, "research_paper_outline.yaml")
        with open(output_file, "w") as file:
            yaml.dump({"subsections": outline_data}, file, default_flow_style=False)
        return output_file

    @staticmethod
    def generate_queries(queries):
        query_data = []
        for i, query in enumerate(queries, start=1):
            query_result = []
            for j in range(1, 6):
                query_result.append(
                    {
                        f"Paper {j}": {
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
                        }
                    }
                )
            query_data.append(
                {
                    "query_number": i,
                    "query_content": query,
                    "query_result": query_result,
                }
            )
        return query_data
