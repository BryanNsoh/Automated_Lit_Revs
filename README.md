# Academic Query Assistant

This project is an AI-enhanced tool designed to assist researchers in exploring academic literature. It integrates with academic databases to provide grounded answers to research questions, offering a starting point for deeper investigation.

## Features

- AI-assisted query generation based on user input
- Integration with academic databases (CORE and arXiv)
- Basic paper analysis and relevance ranking
- Synthesis of key points from retrieved papers
- User-friendly Streamlit web interface

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
- `analyze_papers.py`: Basic analysis and ranking of retrieved papers
- `synthesize_results.py`: Synthesizes key points from analyzed papers
- `models.py`: Pydantic models for data structures
- `llm_api_handler.py`: Handles interactions with language models
- `logger_config.py`: Logging configuration
- `misc_utils.py`: Miscellaneous utility functions

## Dependencies

- Python 3.7+
- Streamlit
- OpenAI API
- Anthropic API
- aiohttp
- pydantic
- python-dotenv
- PyMuPDF

For a complete list of dependencies, see `requirements.txt`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Acknowledgements

This project uses the CORE API and arXiv API for academic paper searches. We thank these services for providing access to their databases.
looks kinda dry do we need to put dependencies in readme. howw would u improve this?
You're right, we can make the README more engaging and focus on the key aspects that would interest potential users or contributors. Here's an improved version that's more concise and engaging:

# Academic Query Assistant 🎓🔍

Supercharge your research with AI-powered academic exploration! This tool helps researchers quickly dive into academic literature, providing grounded answers to research questions and a springboard for deeper investigation.

## 🚀 Key Features

- 🧠 AI-assisted query generation
- 🔗 Integration with CORE and arXiv databases
- 📊 Smart paper analysis and ranking
- 📝 Synthesis of key points from papers
- 🖥️ User-friendly web interface

## 🛠️ Quick Start

1. Clone the repo:
   ```
   git clone https://github.com/BryanNsoh/Academic_Query_Assistant.git
   cd Academic_Query_Assistant
   ```

2. Set up your environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys (see `.env.example` for format)

4. Launch the app:
   ```
   streamlit run streamlit_app.py
   ```

5. Open your browser and start exploring!

## 🧩 How It Works

1. Enter your research question
2. Choose your preferred academic database(s)
3. Set the number of results to retrieve
4. Click "Generate Response"
5. Explore relevant papers and synthesized insights

## 🤝 Contributing

Got ideas? We'd love your input! Feel free to fork, create a feature branch, and submit a pull request.

## 📜 License

This project is open-source under the [MIT License](LICENSE).

## 🙏 Acknowledgements

Special thanks to CORE and arXiv for providing access to their valuable academic databases.