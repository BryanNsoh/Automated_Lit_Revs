"""
This script processes JSON files containing hierarchical data related to irrigation management and
inserts the data into a SQLite database. The script follows a specific data flow and schema to
organize and store the information.

Data Flow:
1. The script starts by checking if the 'searches' folder exists. If not, it prints a message and exits.
2. If the 'searches' folder exists, the script iterates through its subfolders, looking for folders
   that start with 'sec' and end with '_results'.
3. For each 'sec*_results' folder, the script checks if it contains any JSON files. If no JSON files
   are found, it prints a message and moves on to the next folder.
4. If JSON files are found, the script iterates through each file that starts with 'outline_' and
   ends with '.json'.
5. For each JSON file, the script loads its content and checks if the data list is empty. If empty,
   it prints a message and moves on to the next file.
6. If the data list is not empty, the script creates a separate SQLite database for each JSON file,
   with the database name derived from the JSON file name (e.g., 'outline_1.db').
7. The script creates the necessary tables in the database using the 'create_tables' function.
8. The script then inserts the data into the database tables based on the hierarchical structure of
   the JSON data:
   - The first element of the data list is considered the document node and inserted into the 'nodes'
     table with a 'document' node_type.
   - The 'subsections' of the document are iterated, and each subsection is inserted into the 'nodes'
     table with a 'section' node_type, referencing the document node as its parent.
   - Within each subsection, the 'point*' elements are iterated, and each point is inserted into the
     'nodes' table with a 'point' node_type, referencing the corresponding subsection as its parent.
   - For each point, the 'query*' elements are iterated, and each query is inserted into the 'nodes'
     table with a 'query' node_type, referencing the corresponding point as its parent.
   - For each query, a query result is inserted into the 'filtered_query_results' table, referencing the query node.
     The DOI, title, full text, BibTeX, PDF location, journal, citation count, and relevance score entries
     are also stored in the 'filtered_query_results' table.
   - For each query result, multiple result data entries are inserted into the 'result_data' table,
     referencing the query result. Each result data entry contains a chunk text, explanation, and
     overall explanation.
9. After processing each JSON file, the changes are committed to the database, and the database
   connection is closed.

Schema:
The script creates three tables in each SQLite database:

1. 'nodes' table:
   - node_id (INTEGER): Primary key for uniquely identifying each node.
   - parent_id (INTEGER): Foreign key referencing the node_id of the parent node.
   - node_type (TEXT): Indicates the type of node ('document', 'section', 'point', or 'query').
   - title (TEXT): Stores the title of the node (only applicable to 'document' and 'section' nodes).
   - text (TEXT): Stores the text content of the node (only applicable to 'point' nodes).
   - query (TEXT): Stores the query string (only applicable to 'query' nodes).
   - query_result (TEXT): Stores the query result (currently empty, to be populated later).

2. 'filtered_query_results' table:
   - result_id (INTEGER): Primary key for uniquely identifying each query result.
   - query_id (INTEGER): Foreign key referencing the node_id of the corresponding query node.
   - doi (TEXT): Stores the DOI of the query result.
   - title (TEXT): Stores the title of the query result.
   - full_text (TEXT): Stores the full text of the query result.
   - bibtex (TEXT): Stores the BibTeX entry of the query result.
   - pdf_location (TEXT): Stores the location of the PDF file associated with the query result.
   - journal (TEXT): Stores the journal information of the query result.
   - citation_count (INTEGER): Stores the citation count of the query result.
   - relevance_score (REAL): Stores the relevance score of the query result.

3. 'result_data' table:
   - data_id (INTEGER): Primary key for uniquely identifying each result data.
   - result_id (INTEGER): Foreign key referencing the result_id of the corresponding query result.
   - chunk_text (TEXT): Stores the text chunk of the result data.
   - explanation (TEXT): Stores the explanation of the result data.
   - overall_explanation (TEXT): Stores the overall explanation of the result data.

The relationships between the tables are as follows:
- Each 'document' node can have multiple 'section' nodes as children.
- Each 'section' node can have multiple 'point' nodes as children.
- Each 'point' node can have multiple 'query' nodes as children.
- Each 'query' node has one corresponding 'query_result' entry.
- Each 'query_result' entry can have multiple 'result_data' entries.

This hierarchical structure allows for organizing and storing the irrigation management data in a
structured manner, facilitating further analysis and processing.
"""

import os
import json
import sqlite3


# Function to create the database tables
def create_tables(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nodes (
            node_id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            node_type TEXT,
            title TEXT,
            text TEXT,
            query TEXT,
            query_result TEXT,
            FOREIGN KEY (parent_id) REFERENCES nodes(node_id)
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS filtered_query_results (
            result_id INTEGER PRIMARY KEY,
            query_id INTEGER,
            doi TEXT,
            title TEXT,
            full_text TEXT,
            bibtex TEXT,
            pdf_location TEXT,
            journal TEXT,
            citation_count INTEGER,
            relevance_score REAL,
            FOREIGN KEY (query_id) REFERENCES nodes(node_id)
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS result_data (
            data_id INTEGER PRIMARY KEY,
            result_id INTEGER,
            chunk_text TEXT,
            explanation TEXT,
            overall_explanation TEXT,
            FOREIGN KEY (result_id) REFERENCES filtered_query_results(result_id)
        )
    """
    )


# Function to insert a node into the nodes table
def insert_node(cursor, parent_id, node_type, title, text, query):
    cursor.execute(
        """
        INSERT INTO nodes (parent_id, node_type, title, text, query)
        VALUES (?, ?, ?, ?, ?)
    """,
        (parent_id, node_type, title, text, query),
    )
    return cursor.lastrowid


# Function to insert a query result into the filtered_query_results table
def insert_query_result(
    cursor,
    query_id,
    doi,
    title,
    full_text,
    bibtex,
    pdf_location,
    journal,
    citation_count,
    relevance_score,
):
    cursor.execute(
        """
        INSERT INTO filtered_query_results (query_id, doi, title, full_text, bibtex, pdf_location, journal, citation_count, relevance_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            query_id,
            doi,
            title,
            full_text,
            bibtex,
            pdf_location,
            journal,
            citation_count,
            relevance_score,
        ),
    )
    return cursor.lastrowid


# Function to insert result data into the result_data table
def insert_result_data(cursor, result_id, chunk_text, explanation, overall_explanation):
    cursor.execute(
        """
        INSERT INTO result_data (result_id, chunk_text, explanation, overall_explanation)
        VALUES (?, ?, ?, ?)
    """,
        (result_id, chunk_text, explanation, overall_explanation),
    )


# Check if the searches folder exists
searches_folder = "searches"
if not os.path.exists(searches_folder):
    print(f"The '{searches_folder}' folder does not exist.")
else:
    # Iterate through the sections in the searches folder
    for section_folder in os.listdir(searches_folder):
        if section_folder.startswith("sec") and section_folder.endswith("_results"):
            section_path = os.path.join(searches_folder, section_folder)

            # Check if the section folder contains any JSON files
            json_files = [
                file for file in os.listdir(section_path) if file.endswith(".json")
            ]
            if not json_files:
                print(f"No JSON files found in the folder: {section_path}")
                continue

            # Iterate through the JSON files in the section folder
            for file in json_files:
                if file.startswith("outline_") and file.endswith(".json"):
                    file_path = os.path.join(section_path, file)
                    with open(file_path, "r") as f:
                        data = json.load(f)

                        # Check if the data list is not empty
                        if not data:
                            print(f"Skipping empty JSON file: {file_path}")
                            continue

                        # Create a separate database for each JSON file
                        db_name = f"{os.path.splitext(file)[0]}.db"
                        db_path = os.path.join(section_path, db_name)

                        # Delete the existing database file if it exists
                        if os.path.exists(db_path):
                            os.remove(db_path)

                        # Create a new database connection
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()

                        # Create the tables in the database
                        create_tables(cursor)

                        # Insert the document node
                        document_id = insert_node(
                            cursor, None, "document", data[0]["title"], None, None
                        )

                        # Iterate through the subsections
                        for subsection in data[0]["subsections"]:
                            # Insert the subsection node
                            subsection_id = insert_node(
                                cursor,
                                document_id,
                                "section",
                                subsection["title"],
                                None,
                                None,
                            )

                            # Iterate through the points
                            for point_key, point_data in subsection.items():
                                if point_key.startswith("point"):
                                    # Insert the point node
                                    point_id = insert_node(
                                        cursor,
                                        subsection_id,
                                        "point",
                                        None,
                                        point_data["text"],
                                        None,
                                    )

                                    # Iterate through the queries
                                    for query_key, query_text in point_data.items():
                                        if query_key.startswith("query"):
                                            # Insert the query node
                                            query_id = insert_node(
                                                cursor,
                                                point_id,
                                                "query",
                                                None,
                                                None,
                                                query_text,
                                            )

                                            # Insert query result
                                            doi = ""  # Replace with actual DOI
                                            title = ""  # Replace with actual title
                                            full_text = (
                                                ""  # Replace with actual full text
                                            )
                                            bibtex = ""  # Replace with actual BibTeX
                                            pdf_location = (
                                                ""  # Replace with actual PDF location
                                            )
                                            journal = ""  # Replace with actual journal
                                            citation_count = (
                                                0  # Replace with actual citation count
                                            )
                                            relevance_score = 0.0  # Replace with actual relevance score
                                            result_id = insert_query_result(
                                                cursor,
                                                query_id,
                                                doi,
                                                title,
                                                full_text,
                                                bibtex,
                                                pdf_location,
                                                journal,
                                                citation_count,
                                                relevance_score,
                                            )

                                            # Insert result data (multiple entries per query result)
                                            chunk_text = (
                                                ""  # Replace with actual chunk text
                                            )
                                            explanation = (
                                                ""  # Replace with actual explanation
                                            )
                                            overall_explanation = ""  # Replace with actual overall explanation
                                            insert_result_data(
                                                cursor,
                                                result_id,
                                                chunk_text,
                                                explanation,
                                                overall_explanation,
                                            )

                        # Commit the changes and close the connection for the current JSON file
                        conn.commit()
                        conn.close()
