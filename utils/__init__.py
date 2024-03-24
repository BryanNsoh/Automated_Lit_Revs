"""
__init__.py
This file ensures that the 'utils' directory is treated as a Python module.
"""

"""
The YAML structure provided consists of a single top-level key named subsections, which contains a list of items. Each item in this list represents a Point, identified numerically (Point 1, Point 2, etc.). Below is a detailed breakdown of the hierarchical structure:

Top Level

subsections: A list containing items, each of which represents a subsection of content.
Second Level (Points)

Each item within subsections is a Point, denoted by - points: and further identified by a title (e.g., Point 1, Point 2, etc.).
Third Level (Content within Points)

Each Point contains:
google_queries: A list of dictionaries. Each dictionary represents a Google search query and contains a query string, a query_id string, and a responses list.
point_content: A string that describes the content or focus of the Point.
scopus_queries: A list of dictionaries similar to google_queries. Each dictionary represents a Scopus search query and contains a query string, a query_id string, and a responses list.
Fourth Level (Query Responses)

Within each google_queries and scopus_queries dictionary, the responses list contains dictionaries, each representing an individual response to the query. These dictionaries include keys such as DOI, authors, citation_count, full_citation, full_text, inline_citation, journal, pdf_link, publication_year, response_id, and title, most of which are strings or lists, and some may be integers.
This structure is repeated for each Point within the subsections. The Points are numbered sequentially and each contains its unique set of Google and Scopus queries along with their respective responses and a brief content description. Each query within the google_queries and scopus_queries lists is identified by a unique query_id and contains multiple responses, each response structured consistently across the dataset.
"""

"""The YAML structure represents a hierarchical organization of data related to irrigation management. It consists of multiple levels of nesting, with each level providing more specific information or details.

At the top level, we have the "subsections" key, which contains a list of subsections. Each subsection represents a high-level topic or category within the overall subject of irrigation management.

Within each subsection, there is a "points" key, which holds a list of points. Each point represents a specific aspect, concept, or item related to the subsection it belongs to. Points are the main units of information within the YAML structure.

Each point is represented as a dictionary with a single key-value pair. The key of this pair is the title or name of the point, providing a brief description or identifier for that particular point. The value associated with the point title is another dictionary that contains further details and information related to that point.

Inside each point dictionary, there are two optional keys: "google_queries" and "scopus_queries". These keys represent different types of queries or searches associated with the point.

The "google_queries" key, if present, contains a list of dictionaries representing Google search queries related to the point. Each dictionary within this list corresponds to a specific Google query and includes the following information:
"query": The actual query string used for the Google search.
"query_id": A unique identifier for the query, prefixed with "google_".
"responses": A list of dictionaries representing the search results or responses obtained from the Google query. Each response dictionary contains various fields such as "DOI", "authors", "citation_count", "full_citation", "full_text", "inline_citation", "journal", "pdf_link", "publication_year", "response_id", and "title".
Similarly, the "scopus_queries" key, if present, contains a list of dictionaries representing Scopus search queries related to the point. Each dictionary within this list corresponds to a specific Scopus query and follows a structure similar to the Google queries, with fields like "query", "query_id", and "responses".
The "point_content" key within each point dictionary provides a brief description or summary of the content or focus of that particular point.

In the code, the process_queries function traverses this YAML structure to process the queries and retrieve relevant information. It starts by iterating over the subsections, then moves on to the points within each subsection. For each point, it checks for the presence of "google_queries" and "scopus_queries" keys. If found, it processes the corresponding queries using the get_scholar_data function (for Google queries) or performs Scopus query processing (not shown in the code snippet). The retrieved results are stored back into the "responses" field of each query dictionary.

The hierarchy flows from subsections to points, and within each point, it branches into Google queries and Scopus queries. The queries are processed individually, and their results are stored within the respective query dictionaries, maintaining the overall structure and organization of the YAML data.

This hierarchical and nested structure allows for a clear and organized representation of the data, enabling easy access and retrieval of specific information related to irrigation management based on subsections, points, and associated queries."""
