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
                        "alex_queries": self.generate_queries(point["google_queries"]),
                    }
                }
                subsection_data["points"].append(point_data)
            outline_data.append(
                subsection_data
            )  # Move this line inside the subsection loop

        output_file = os.path.join(self.output_directory, "research_paper_outline.yaml")
        with open(output_file, "w") as file:
            yaml.dump({"subsections": outline_data}, file, default_flow_style=False)
        return output_file

    @staticmethod
    def generate_queries(queries):
        query_data = []
        for i, query in enumerate(queries, start=1):
            query_result = []
            for j in range(1, 3):
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


# calling the class
if __name__ == "__main__":
    json_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline.json"
    output_directory = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3"
    generator = ResearchPaperOutlineGenerator(json_file, output_directory)
    generator.generate_outline()
    print("Research paper outline generated successfully!")
