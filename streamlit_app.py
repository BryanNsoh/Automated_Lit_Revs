# streamlit_app.py

import streamlit as st
import asyncio
from get_search_queries import QueryGenerator
from core_search import CORESearch
from analyze_papers import PaperAnalyzer
from synthesize_results import ResultSynthesizer
from models import SearchQueries, SearchResults, RankedPapers
import time

st.set_page_config(page_title="AI-Powered Literature Review Assistant", layout="wide")

@st.cache_resource
def get_llm_handler():
    from llm_api_handler import LLMAPIHandler
    return LLMAPIHandler()

st.title("AI-Powered Literature Review Assistant")

# Sidebar Explanation
st.sidebar.markdown("""
## How it works

1. **Query Generation**: Your input is used to generate specific search queries.
2. **Literature Search**: These queries are used to search the CORE academic database.
3. **Paper Analysis**: The retrieved papers are analyzed for relevance and content.
4. **Result Synthesis**: The findings are synthesized into a comprehensive literature review.

This process is powered by advanced AI models and natural language processing techniques.
""")

st.markdown("""
Welcome to the **AI-Powered Literature Review Assistant**! Enter your research query below, and the AI will search the CORE academic database, analyze relevant papers, and synthesize the results for you.
""")

user_query = st.text_area("Enter your research query here:", height=150)

async def process(user_query: str):
    llm_handler = get_llm_handler()

    # Generate Search Queries
    query_generator = QueryGenerator()
    search_queries: SearchQueries = await query_generator.generate_queries(user_query, num_queries=5)
    with st.expander("Click to see Generated Search Queries"):
        st.json(search_queries.model_dump())

    # Search in CORE
    core_search = CORESearch(max_results=10)
    search_results: SearchResults = await core_search.search_and_parse_queries(search_queries)
    with st.expander("Click to see Search Results"):
        st.json(search_results.model_dump())

    # Analyze Papers
    paper_analyzer = PaperAnalyzer()
    ranked_papers: RankedPapers = await paper_analyzer.analyze_papers(search_results, user_query)

    # Display ranked papers in an expander
    with st.expander("Click to see Ranked Papers"):
        for i, paper in enumerate(ranked_papers.papers, 1):
            st.write(f"Paper {i}:")
            st.write(f"Title: {paper.title}")
            st.write(f"Authors: {', '.join(paper.authors)}")
            st.write(f"Year: {paper.year}")
            st.write(f"Relevance Score: {paper.relevance_score}")
            st.write(f"Analysis: {paper.analysis}")
            st.write("Relevant Quotes:")
            for quote in paper.relevant_quotes:
                st.write(f"- {quote}")
            st.write("---")

    result_synthesizer = ResultSynthesizer()
    synthesis = await result_synthesizer.synthesize(ranked_papers, user_query)

    # Display the final synthesis as markdown
    st.subheader("Literature Review Synthesis")
    st.markdown(synthesis)

# Async function to handle form submissions
async def handle_submit(user_query: str):
    await process(user_query)

# Function to execute async tasks properly within Streamlit
def run_async_task(coro):
    """
    Schedule the execution of an async coroutine within the existing event loop.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # If there's a running loop, create a task
        return asyncio.create_task(coro)
    else:
        # If no loop is running, run the coroutine
        return loop.run_until_complete(coro)

# Button to submit the query
if st.button("Submit Query"):
    if not user_query.strip():
        st.error("Please enter a valid research query.")
    else:
        with st.spinner("Processing your query. This may take a few minutes..."):
            try:
                # Create a placeholder for the success message
                message_placeholder = st.empty()
                message_placeholder.success("Query processing has started. Please check the results below as they become available.")
                
                # Schedule the async 'handle_submit' function
                run_async_task(handle_submit(user_query))
                
                # Wait for a short time to allow results to populate
                time.sleep(5)
                
                # Clear the success message
                message_placeholder.empty()
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)