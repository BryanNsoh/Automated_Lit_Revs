import sys
import os
import aiohttp
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from get_search_queries import QueryGenerator
from analyze_papers import PaperRanker
from synthesize_results import QueryProcessor
from core_search import CORESearch
from misc_utils import get_api_keys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class ResearchQueryProcessor:
    def __init__(self):
        self.api_keys = get_api_keys(source="local" if os.getenv("ENVIRONMENT") == "local" else "env")

    async def chatbot_response(self, message: str) -> str:
        async with aiohttp.ClientSession() as session:
            logger.info("Generating search queries...")
            query_generator = QueryGenerator(session)
            search_queries = await query_generator.generate_queries(message)

            logger.info("Searching in CORE...")
            core_search = CORESearch(max_results=5)
            search_results = await core_search.search_and_parse_json(search_queries)

            logger.info("Analyzing papers...")
            paper_ranker = PaperRanker(session)
            analyzed_papers = await paper_ranker.process_queries(
                search_results, message
            )

            logger.info("Synthesizing results...")
            query_processor = QueryProcessor(session)
            synthesized_results = await query_processor.process_query(
                message, analyzed_papers
            )

            final_response = f"{synthesized_results}"
            logger.info(f"Final response: {final_response}")
            return final_response


processor = ResearchQueryProcessor()


@app.get("/", response_class=HTMLResponse)
async def get_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI-Powered Literature Review Assistant</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f4f8;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                min-height: 100vh;
                font-size: 16px;
            }
            .container {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 1.5rem;
                margin: 1rem;
                max-width: 800px;
                width: 100%;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 0.5rem;
                font-size: 1.8em;
            }
            .description {
                color: #34495e;
                text-align: center;
                margin-bottom: 1rem;
            }
            textarea {
                width: 100%;
                padding: 0.5rem;
                margin-bottom: 0.5rem;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                resize: vertical;
                font-size: 1em;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #2980b9;
            }
            #result {
                margin-top: 1rem;
                white-space: pre-wrap;
                background-color: #ecf0f1;
                padding: 1rem;
                border-radius: 5px;
                display: none;
                font-size: 1em;
            }
            .loader {
                text-align: center;
                margin: 20px auto;
                display: none;
            }
            .loader-text {
                margin-bottom: 10px;
            }
            .spinner {
                border: 5px solid #f3f3f3;
                border-top: 5px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI-Powered Literature Review Assistant</h1>
            <p class="description">
                Welcome to our advanced research tool! Here's how it works:
                <br>
                1. Enter your research query in the box below.
                <br>
                2. Our AI will search the CORE academic database (currently limited to open access papers).
                <br>
                3. You'll receive a synthesized answer based on the most relevant peer-reviewed research.
            </p>
            <form id="queryForm">
                <textarea id="queryText" rows="4" placeholder="Enter your research query here (e.g., 'What are the latest treatments for heart disease?')" required></textarea>
                <button type="button" onclick="submitQuery()">Submit Query</button>
            </form>
            <div class="loader" id="loader">
                <p class="loader-text" id="loaderText">Searching database...</p>
                <div class="spinner"></div>
            </div>
            <div id="result"></div>
        </div>
        <script>
            async function submitQuery() {
                const query = document.getElementById('queryText').value;
                document.getElementById('result').style.display = 'none';
                document.getElementById('loader').style.display = 'block';
                
                const loadingSteps = [
                    "Searching database...",
                    "Analyzing papers...",
                    "Synthesizing results..."
                ];
                let currentStep = 0;
                
                const loadingInterval = setInterval(() => {
                    document.getElementById('loaderText').innerText = loadingSteps[currentStep];
                    currentStep = (currentStep + 1) % loadingSteps.length;
                }, 3000);
                
                try {
                    const response = await fetch('/process_query/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: 'query=' + encodeURIComponent(query)
                    });
                    const result = await response.json();
                    clearInterval(loadingInterval);
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').innerHTML = result.result;
                } catch (error) {
                    clearInterval(loadingInterval);
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').innerHTML = "An error occurred. Please try again.";
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/process_query/")
async def process_query(query: str = Form(...)):
    try:
        logger.info(f"Received query: {query}")
        result = await processor.chatbot_response(query)
        logger.info(f"Processed query successfully")
        return {"result": result}
    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
