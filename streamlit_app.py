# streamlit_app.py

import streamlit as st
import asyncio
from get_search_queries import QueryGenerator
from searchers import CORESearch, ArXivSearch
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

st.sidebar.markdown("""
## How it works

1. **Query Generation**: Your input is used to generate specific search queries.
2. **Literature Search**: These queries are used to search academic databases.
3. **Paper Analysis**: The retrieved papers are analyzed for relevance and content.
4. **Result Synthesis**: The findings are synthesized into a comprehensive literature review.

This process is powered by advanced AI models and natural language processing techniques.
""")

st.markdown("""
Welcome to the **AI-Powered Literature Review Assistant**! Enter your research query below, and the AI will search academic databases, analyze relevant papers, and synthesize the results for you.
""")

user_query = st.text_area("Enter your research query here:", height=150)

search_engine = st.selectbox("Choose search engine:", ["CORE", "arXiv", "Both"])

num_results = st.number_input("Number of results per search engine:", min_value=1, max_value=10, value=10)

async def process(user_query: str, search_engine: str, num_results: int):
    llm_handler = get_llm_handler()

    query_generator = QueryGenerator()
    search_queries: SearchQueries = await query_generator.generate_queries(user_query, num_queries=5)
    with st.expander("Click to see Generated Search Queries"):
        st.json(search_queries.model_dump())

    search_results = SearchResults(results=[])
    if search_engine in ["CORE", "Both"]:
        core_search = CORESearch(max_results=num_results)
        core_results = await core_search.search_and_parse_queries(search_queries)
        search_results.results.extend(core_results.results[:num_results])

    if search_engine in ["arXiv", "Both"]:
        arxiv_search = ArXivSearch(max_results=num_results)
        arxiv_results = await arxiv_search.search_and_parse_queries(search_queries)
        search_results.results.extend(arxiv_results.results[:num_results])

    with st.expander("Click to see Search Results"):
        st.json(search_results.model_dump())

    paper_analyzer = PaperAnalyzer()
    ranked_papers: RankedPapers = await paper_analyzer.analyze_papers(search_results, user_query)

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

    st.subheader("Literature Review Synthesis")
    st.markdown(synthesis)

async def handle_submit(user_query: str, search_engine: str, num_results: int):
    await process(user_query, search_engine, num_results)

def run_async_task(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        return asyncio.create_task(coro)
    else:
        return loop.run_until_complete(coro)

if st.button("Submit Query"):
    if not user_query.strip():
        st.error("Please enter a valid research query.")
    else:
        with st.spinner("Processing your query. This may take a few minutes..."):
            try:
                message_placeholder = st.empty()
                message_placeholder.success("Query processing has started. Please check the results below as they become available.")
                
                run_async_task(handle_submit(user_query, search_engine, num_results))
                
                time.sleep(5)
                
                message_placeholder.empty()
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)