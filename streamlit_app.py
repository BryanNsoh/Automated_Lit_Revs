# streamlit_app.py

import streamlit as st
import asyncio
import aiohttp
import json
from analyze_papers import PaperRanker
from get_search_queries import QueryGenerator
from synthesize_results import QueryProcessor
from core_search import CORESearch

# Function to run async functions in Streamlit
def run_async(coroutine):
    return asyncio.run(coroutine)

st.set_page_config(page_title="Automated Literature Reviews", layout="wide")

st.title("AI-Powered Literature Review Assistant")

st.markdown("""
Welcome to the **Automated Literature Review Assistant**! Enter your research query below, and the AI will search the CORE academic database, analyze relevant papers, and synthesize the results for you.
""")

user_query = st.text_area("Enter your research query here:", height=150)

if st.button("Submit Query"):
    if not user_query.strip():
        st.error("Please enter a valid research query.")
    else:
        with st.spinner("Processing your query. This may take a few minutes..."):
            async def process():
                async with aiohttp.ClientSession() as session:
                    # Generate Search Queries
                    query_generator = QueryGenerator(session)
                    search_queries = await query_generator.generate_queries(user_query)

                    # Search in CORE
                    core_search = CORESearch(max_results=5)
                    search_results = await core_search.search_and_parse_json(search_queries)

                    # Analyze Papers
                    paper_ranker = PaperRanker(session)
                    analyzed_papers = await paper_ranker.process_queries(search_results, user_query)

                    # Synthesize Results
                    query_processor = QueryProcessor(session)
                    synthesized_results = await query_processor.process_query(user_query, analyzed_papers)

                    return synthesized_results

            try:
                results = run_async(process())
                st.success("Query processed successfully!")
                st.markdown(results, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
