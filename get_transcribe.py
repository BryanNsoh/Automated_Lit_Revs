import os
import subprocess
from scidownl import scihub_download


def sanitize_filename(filename):
    """
    Sanitizes the filename by removing unwanted characters,
    including slashes and colons, and replacing them with underscores.
    """
    return "".join([c if c.isalnum() else "_" for c in filename])


def process_paper(directory, doi):
    # Sanitize the DOI to be file-system friendly
    sanitized_doi = sanitize_filename(doi)
    pdf_path = os.path.join(directory, f"{sanitized_doi}.pdf")

    # Download the research paper PDF using SciDownl
    scihub_download(doi, paper_type="doi", out=pdf_path)

    # Specify the output directory for Nougat
    output_directory = os.path.join(directory, "nougat_output")

    # Make sure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Print when Nougat processing begins
    print(f"Starting Nougat processing for {doi}...")

    # Process the PDF using Nougat via subprocess
    command = f'nougat "{pdf_path}" -o "{output_directory}"'
    process = subprocess.run(
        command, shell=True, check=True, text=True, capture_output=True
    )

    # Assuming the command outputs the result to stdout or a specific file, handle accordingly
    print(f"Nougat processing completed for: {doi}")
    # Print standard output (stdout) if needed
    # print(process.stdout)


def main():
    directory = "output"  # Specify the output directory path here
    doi = "https://doi.org/10.3390/s21123942"  # Specify the DOI of the research paper here

    if not os.path.exists(directory):
        os.makedirs(directory)

    process_paper(directory, doi)


if __name__ == "__main__":
    main()
