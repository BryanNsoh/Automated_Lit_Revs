```markdown
# Automated Search and Curation for Systematic Literature Reviews

This repository contains a set of Python scripts for automating the search and curation process in systematic literature reviews. The system leverages APIs, web scraping, and natural language processing to streamline the identification, retrieval, and analysis of relevant research papers.

## Features

- Automated search query generation based on a structured YAML outline
- Integration with Scopus and OpenAlex APIs for comprehensive literature search
- Web scraping capabilities for extracting full-text content from URLs and DOIs
- Asynchronous processing for efficient handling of multiple queries and requests
- Relevance scoring and filtering of retrieved papers using machine learning models
- Modular design allowing easy extension and customization

## Prerequisites

- Python 3.7+
- Required libraries: `aiohttp`, `aiofiles`, `asyncio`, `yaml`, `fitz`, `selenium`, `undetected_chromedriver`

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/automated-literature-review.git
   ```

2. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   - Create a `api_keys.json` file in the `keys` directory.
   - Add your Scopus API key, OpenAlex API key, and other required keys to the file.

## Usage

1. Prepare your literature review outline in a YAML file following the provided structure.

2. Run the main script with the appropriate arguments:
   ```
   python main.py --outline outline.yaml --output output_directory
   ```

3. The system will process the outline, generate search queries, retrieve papers from APIs, scrape full-text content, and perform relevance scoring.

4. The curated papers will be saved in the specified output directory, organized by subsections and points.

## Code Structure

- `main.py`: The entry point of the system, orchestrating the overall process.
- `utils/`: Directory containing utility scripts for various tasks.
  - `extract_relevant_papers.py`: Extracts relevant papers based on relevance scores.
  - `llm_api_handler.py`: Handles interactions with language model APIs for query generation and relevance scoring.
  - `openalex_search.py`: Performs paper search using the OpenAlex API.
  - `scopus_search.py`: Performs paper search using the Scopus API.
  - `web_scraper.py`: Scrapes full-text content from URLs and DOIs.
  - `yaml_iterator.py`: Iterates over the YAML outline and processes each section and point.

## Extensibility

The modular design of the system allows for easy extension and customization:

- Add new search APIs by creating a new module in the `utils/` directory and integrating it into the main process.
- Customize the relevance scoring algorithm by modifying the `llm_api_handler.py` script.
- Extend the web scraping capabilities by updating the `web_scraper.py` script.

## License

This project is licensed under the [MIT License](LICENSE).
```
