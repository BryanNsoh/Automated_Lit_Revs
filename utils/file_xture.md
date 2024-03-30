---
markmap:
  colorFreezeLevel: 2
---

# File Structure

- `utils/`
  - `__init__.py`: Marks the directory as a Python module
  - `copy_all_code.py`: Copies contents of all Python files to a single text file
  - `doi_scraper_new.py`: Scrapes content from DOI links using Pyppeteer
  - `google_scholar_search.py`: Performs Google Scholar searches and extracts relevant data
  - `llm_api_handler.py`: Handles interactions with language model APIs (Gemini, Claude)
  - `misc_utils.py`: Contains utility functions for preparing text for JSON
  - `openalex_search.py`: Performs searches on the OpenAlex API and extracts relevant data
  - `populate_search_queries.py`: Generates search queries for each point in the YAML data using LLM_APIHandler
  - `populate_search_results.py`: Processes search queries, retrieves results from Scopus and OpenAlex APIs, and updates YAML data
  - `prompts.py`: Contains prompt templates and guidance for generating search queries
  - `research_paper_outline_generator.py`: Generates a YAML-formatted research paper outline from a JSON input file
  - `scopus_search.py`: Performs searches on the Scopus API and extracts relevant data
  - `web_scraper.py`: Scrapes content from web pages using Undetected Chromedriver
  - `yaml_iterator.py`: Provides a class for iterating over and updating the YAML data structure

- `documents/`
  - `section*/`
    - `research_paper_outline.yaml`: Generated YAML outline for the research paper
    - `outline_queries.yaml`: Updated YAML file with generated search queries
    - `search_results/`: Directory containing individual YAML files with search results for each query

- `api_keys.json`: JSON file containing API keys for Scopus, Gemini, and Claude

- `main.py`: Entry point of the program, orchestrates the execution of various components