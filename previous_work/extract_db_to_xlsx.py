import os
import glob
import sqlite3
import pandas as pd
import re


def remove_illegal_characters(text):
    if text is None:
        return ""
    illegal_chars = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")
    return illegal_chars.sub("", str(text))


def extract_data_and_write_to_xlsx(db_path, xlsx_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to extract the required data
    query = """
        SELECT 
            d.title AS document_title,
            s.title AS section_title,
            p.text AS point_text,
            q.query,
            r.doi, 
            r.title, 
            r.full_text, 
            r.bibtex, 
            r.pdf_location, 
            r.journal, 
            r.citation_count, 
            r.relevance_score
        FROM nodes AS d
        JOIN nodes AS s ON d.node_id = s.parent_id
        JOIN nodes AS p ON s.node_id = p.parent_id
        JOIN nodes AS q ON p.node_id = q.parent_id
        JOIN filtered_query_results AS r ON q.node_id = r.query_id
        WHERE d.node_type = 'document'
            AND s.node_type = 'section'
            AND p.node_type = 'point'
            AND q.node_type = 'query'
    """

    # Execute the query and fetch the results
    results = cursor.execute(query).fetchall()

    # Create a DataFrame from the results
    columns = [
        "document_title",
        "section_title",
        "point_text",
        "query",
        "doi",
        "title",
        "full_text",
        "bibtex",
        "pdf_location",
        "journal",
        "citation_count",
        "relevance_score",
    ]
    df = pd.DataFrame(results, columns=columns)

    # Remove illegal characters from the DataFrame
    df = df.applymap(remove_illegal_characters)

    # Write the DataFrame to an Excel file
    df.to_excel(xlsx_path, index=False)

    # Close the database connection
    conn.close()


def main():
    db_directory = "searches"

    # Check if 'searches' folder exists
    if not os.path.exists(db_directory):
        print("The 'searches' folder does not exist.")
        return

    # Delete existing outline files
    outline_files = glob.glob(
        os.path.join(db_directory, "**", "outline_*.xlsx"), recursive=True
    )
    for file in outline_files:
        os.remove(file)
        print(f"Deleted existing file: {file}")

    # Iterate through each 'sec*_results' subfolder
    for sec_folder in glob.glob(os.path.join(db_directory, "sec*_results")):
        # Iterate through each 'outline_*.db' file in the subfolder
        for db_path in glob.glob(os.path.join(sec_folder, "outline_*.db")):
            base_name = os.path.splitext(os.path.basename(db_path))[0]
            xlsx_path = os.path.join(os.path.dirname(db_path), f"{base_name}.xlsx")

            # Extract data from the database and write to XLSX
            extract_data_and_write_to_xlsx(db_path, xlsx_path)
            print(f"Data extracted to XLSX for database: {db_path}")


if __name__ == "__main__":
    main()
