---
markmap:
  colorFreezeLevel: 2
---

# Data Flow

## Input
- User provides a YAML file containing subsections, points, and initial query information

## Query Generation
- `QueryGenerator` class is instantiated with the path to the input YAML file and the path to the API key file
- `QueryGenerator` loads the YAML data and iterates over each subsection and point
- For each point, `QueryGenerator` calls the `get_queries` method to generate search queries
  - `get_queries` method constructs a prompt using the `get_prompt` function from `prompts.py`
  - The prompt includes the review intention, section intention, point content, section title, subsection title, and search guidance
  - `get_queries` sends the prompt to the `generate_gemini_content` method of `LLM_APIHandler` to generate search queries using the Gemini API
  - The generated queries are parsed and stored back into the YAML structure
- `QueryGenerator` saves the updated YAML data with generated queries to a temporary file and renames it to `outline_queries.yaml`

## Query Processing
- `QueryProcessor` class is instantiated with the path to `outline_queries.yaml`, output folder, API key file, and email
- `QueryProcessor` loads the updated YAML data and iterates over each subsection, point, query type, query ID, and response ID
- For each query, `QueryProcessor` calls the `process_query` method
  - If the query type is "scopus_queries", `process_query` calls the `search_and_parse` method of `ScopusSearch` to search and extract data from the Scopus API
  - If the query type is "alex_queries", `process_query` calls the `search_papers` method of `OpenAlexPaperSearch` to search and extract data from the OpenAlex API
  - The search results are saved as individual YAML files in the `search_results` folder
  - The path to the saved YAML file is updated in the corresponding response object of the YAML data
- `QueryProcessor` saves the final updated YAML data with paths to search result files

## Output
- `outline_queries.yaml`: Updated YAML file with generated search queries
- `search_results/`: Folder containing individual YAML files with search results for each query

## Component Interactions
- `QueryGenerator` uses `LLM_APIHandler` to generate search queries using the Gemini API
- `QueryProcessor` uses `ScopusSearch` and `OpenAlexPaperSearch` to search and extract data from the Scopus and OpenAlex APIs, respectively
- `ScopusSearch` and `OpenAlexPaperSearch` use `WebScraper` to scrape additional data from web pages
- `yaml_iterator.py` provides the `IrrigationData` class for loading, updating, and saving the YAML data throughout the program