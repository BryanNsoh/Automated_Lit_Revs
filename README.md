# Academic Query Assistant

This project is an AI-enhanced tool designed to assist researchers in exploring academic literature. It integrates with academic databases to provide grounded answers to research questions, offering a starting point for deeper investigation.

## Demo

Try out the live demo: [Academic Query Assistant](https://autolitreview.streamlit.app/)

## Features

- AI-assisted query generation based on user input
- Integration with academic databases (CORE and arXiv)
- Advanced paper analysis and relevance ranking
- Synthesis of key points from retrieved papers
- User-friendly Streamlit web interface

## Relevance Ranking Algorithm

The project implements a novel paper ranking algorithm that combines adaptive shuffling with AI-based comparisons:

1. Papers are initially retrieved from academic databases based on relevance to the query.
2. The algorithm employs multiple rounds of ranking to reduce bias:
   - In each round, papers are randomly grouped.
   - An LLM compares papers within each group, assigning relevance scores.
   - Papers are re-shuffled for the next round.
3. Final rankings are determined by aggregating scores across all rounds.
4. The top-ranked papers undergo detailed analysis and synthesis.

This approach aims to provide a fair and thorough assessment of each paper's relevance while mitigating potential biases from initial database ordering or LLM inconsistencies.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/BryanNsoh/Academic_Query_Assistant.git
   cd Academic_Query_Assistant
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the root directory and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   CORE_API_KEY=your_core_api_key
   CORE_API_KEY1=your_additional_core_api_key
   CORE_API_KEY2=your_additional_core_api_key
   CORE_API_KEY3=your_additional_core_api_key
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run streamlit_app.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Enter your research question in the text area provided.

4. Choose the desired search engine (CORE, arXiv, or both) and set the number of results to retrieve.

5. Click the "Generate Response" button to start the process.

6. The app will display relevant papers and a synthesized response based on the retrieved information.

## Project Structure

- `streamlit_app.py`: Main Streamlit application
- `get_search_queries.py`: Generates search queries from user input
- `searchers/`: Contains search modules for academic databases
- `analyze_papers.py`: Analysis and ranking of retrieved papers
- `synthesize_results.py`: Synthesizes key points from analyzed papers
- `models.py`: Pydantic models for data structures
- `llm_api_handler.py`: Handles interactions with language models
- `logger_config.py`: Logging configuration
- `misc_utils.py`: Miscellaneous utility functions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Acknowledgements

This project uses the CORE API and arXiv API for academic paper searches. We thank these services for providing access to their databases.