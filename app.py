import sys
import os
import aiohttp
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from get_search_queries import QueryGenerator
from scopus_search import ScopusSearch
from analyze_papers import PaperRanker
from synthesize_results import QueryProcessor
from web_scraper import WebScraper
from core_search import CORESearch
from misc_utils import get_api_keys

from logger_config import get_logger

logger = get_logger(__name__)

app = FastAPI()


class ResearchQueryProcessor:
    def __init__(self):
        self.api_keys = get_api_keys()

    async def chatbot_response(self, message: str) -> str:
        async with aiohttp.ClientSession() as session:
            responses = []

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
    <html>
    <head>
        <title>Literature Review Agent</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #fefefe;
                color: #333;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                text-align: center;
                border: 2px solid #ff4d4d;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                width: 100%;
                background-color: #fff;
            }
            h1 {
                color: #ff4d4d;
                margin-bottom: 20px;
            }
            textarea {
                width: 100%;
                height: 100px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                resize: none;
                font-size: 16px;
                margin-bottom: 20px;
            }
            button {
                background-color: #ff4d4d;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover {
                background-color: #e63939;
            }
            #result {
                white-space: pre-wrap;
                margin-top: 20px;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Literature Review Agent</h1>
            <form id="queryForm">
                <textarea id="queryText" placeholder="Enter your research query..."></textarea><br>
                <button type="button" onclick="submitQuery()">Submit</button>
            </form>
            <div id="result"></div>
        </div>
        <script>
            async function submitQuery() {
                document.getElementById('result').innerHTML = "Your request has been submitted and is being processed. Please hang tight, this might take a few minutes.";
                const query = document.getElementById('queryText').value;
                const response = await fetch('/process_query/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: 'query=' + encodeURIComponent(query)
                });
                const result = await response.json();
                if (result.status == 'submitted') {
                    document.getElementById('result').innerHTML += '<br>Task ID: ' + result.task_id;
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
        return HTMLResponse(content=result, media_type="text/html")
    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
