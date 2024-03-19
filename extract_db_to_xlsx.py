import sqlite3
import os
import glob
from openpyxl import Workbook
from collections import defaultdict


def extract_data_and_write_to_xlsx(db_path, xlsx_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to extract all required information
    query = """
    SELECT n1.title AS section, n2.title AS subsection, n3.text AS point, n4.query AS query,
       fqr.doi AS doi, fqr.title AS query_title, '' AS full_text, fqr.bibtex, fqr.pdf_location,
       fqr.journal, fqr.citation_count, fqr.relevance_score, (fqr.citation_count * fqr.relevance_score) AS rank,
       CASE 
           WHEN fqr.doi IS NOT NULL AND fqr.doi != '' THEN 'https://doi.org/' || fqr.doi
           ELSE fqr.doi
       END AS adoi_url
    FROM nodes n1
    LEFT JOIN nodes n2 ON n1.node_id = n2.parent_id AND n2.node_type = 'section'
    LEFT JOIN nodes n3 ON n2.node_id = n3.parent_id AND n3.node_type = 'point'
    LEFT JOIN nodes n4 ON n3.node_id = n4.parent_id AND n4.node_type = 'query'
    LEFT JOIN filtered_query_results fqr ON n4.node_id = fqr.query_id
    WHERE n1.node_type = 'document' AND fqr.relevance_score <= 0.2;


    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Process rows to ensure at least 4 entries per point, filling with null values if necessary
    processed_rows = process_rows_to_ensure_minimum_entries(rows)

    # Write the processed data to an XLSX file
    write_to_xlsx(xlsx_path, processed_rows)


def process_rows_to_ensure_minimum_entries(rows):
    # Corrected grouping logic
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Populate the grouped structure
    for row in rows:
        (
            section,
            subsection,
            point,
            query,
            doi,
            query_title,
            full_text,
            bibtex,
            pdf_location,
            journal,
            citation_count,
            relevance_score,
            rank,
            adoi_url,
        ) = row
        key = (section, subsection, point)
        grouped[section][subsection][point].append(row)

    processed_rows = []

    # Process groups to ensure at least 4 entries per point
    for section, subsections in grouped.items():
        for subsection, points in subsections.items():
            for point, entries in points.items():
                num_entries = len(entries)
                filled_entries = 0
                relevant_entries = 0

                for entry in entries:
                    doi, query_title, relevance_score = entry[4:7]

                    # Convert relevance_score to float, default to 0 if empty or None
                    relevance_score = (
                        float(relevance_score)
                        if relevance_score and relevance_score.strip()
                        else 0
                    )

                    if query_title is not None:
                        # Keep the entry as is
                        processed_rows.append(entry)
                        filled_entries += 1
                        relevant_entries += 1
                    else:
                        # Clear specified fields if relevance score < 2 or no DOI/title
                        new_entry = entry[:4] + (None,) * 10
                        processed_rows.append(new_entry)
                        filled_entries += 1

                # If fewer than 4 relevant entries, add filler entries up to 4 total entries
                while filled_entries < 4 and relevant_entries < 4:
                    filler_entry = (entry[0], entry[1], entry[2], None) + (None,) * 10
                    processed_rows.append(filler_entry)
                    filled_entries += 1

    return processed_rows


def write_to_xlsx(xlsx_path, rows):
    wb = Workbook()
    ws = wb.active

    # Write headers
    headers = [
        "SECTION",
        "SUBSECTION",
        "POINT",
        "QUERY",
        "DOI",
        "PAPER_TITLE",
        "RELEVANCE_SCORE",
        "FULL_TEXT",
        "BIBTEX",
        "PDF_LOCATION",
        "JOURNAL",
        "CITATION_COUNT",
        "RANK",
        "ADOI_URL",
    ]
    ws.append(headers)

    # Write rows
    for row in rows:
        ws.append(row)

    # Save the workbook
    wb.save(xlsx_path)


def main():
    db_directory = "searches"

    # Check if 'searches' folder exists
    if not os.path.exists(db_directory):
        print("The 'searches' folder does not exist.")
        return

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
