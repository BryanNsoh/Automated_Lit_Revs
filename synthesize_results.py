import logging
from llm_api_handler import LLMAPIHandler
from models import RankedPapers, RankedPaper
from typing import List
from pydantic import BaseModel

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SynthesisResponse(BaseModel):
    plan: str
    content: str

SYNTHESIS_PROMPT = """
Based on the following analysis of research papers, provide a comprehensive answer to the user's question: "{user_query}"

Paper analyses:
{paper_analyses}

Your response should be in two parts:

1. A brief plan (about 100 words) outlining:
   - Which studies you'll include and why
   - Any studies you'll exclude due to lack of relevance
   - How you plan to directly answer the question in a way the user finds useful
   - The main points you'll cover

2. A detailed response that:
   - Directly answers the user's question using the provided analyses
   - Synthesizes the main points from each relevant paper
   - Identifies common themes or contradictions across the papers
   - Discusses how these findings address the original query
   - Highlights any limitations or areas for further research

Format your detailed response primarily in paragraphs, using a natural writing style. 
Minimize the use of bullet points, lists, or section divisions. 
Convey the information in a way that is easy to understand and use. 
Maintain word economy, using as few words as possible to convey the information while maintaining its clarity and depth.
Every single word should be used with intention and should earn its place in the text.

For citations:
- Use APA-style inline citations
- Include hyperlinks to dois in the inline citations where available for example [author et al. (year)](https://doi.org/10.1234/water.2021.001)
- Add a references section at the end APA style

Respond in the following JSON format:
{{
    "plan": "Your brief plan here",
    "content": "Your full markdown-formatted response here, including references"
}}
"""

class ResultSynthesizer:
    def __init__(self):
        self.llm_api_handler = LLMAPIHandler()
        logger.debug("ResultSynthesizer initialized")

    def _format_paper_analyses(self, papers: List[RankedPaper]) -> str:
        logger.debug(f"Formatting {len(papers)} paper analyses")
        paper_analyses = ""
        for i, paper in enumerate(papers, 1):
            paper_analyses += f"""
Paper {i}:
Title: {paper.title}
Authors: {', '.join(paper.authors)}
publication_year: {paper.publication_year}
doi: {paper.doi}
Relevance Score: {paper.relevance_score}
Analysis: {paper.analysis}
Relevant Quotes:
{self._format_quotes(paper.relevant_quotes)}

"""
        logger.debug("Paper analyses formatted successfully")
        return paper_analyses.strip()

    def _format_quotes(self, quotes: List[str]) -> str:
        logger.debug(f"Formatting {len(quotes)} quotes")
        return "\n".join([f"- {quote}" for quote in quotes])

    async def synthesize(self, ranked_papers: RankedPapers, user_query: str) -> str:
        logger.debug(f"Starting synthesis for query: {user_query}")
        papers = ranked_papers.papers
        logger.debug(f"Number of papers to synthesize: {len(papers)}")

        paper_analyses = self._format_paper_analyses(papers)
        logger.debug("Paper analyses formatted")

        prompt = SYNTHESIS_PROMPT.format(
            user_query=user_query,
            paper_analyses=paper_analyses
        )
        logger.debug("Synthesis prompt created")

        try:
            logger.info(f"Sending request to LLM API for query: {user_query}")
            response = await self.llm_api_handler.async_process(
                prompts=[prompt],
                model="gpt-4o-2024-08-06",
                system_message="You are a helpful assistant tasked with synthesizing research paper analyses.",
                temperature=0.6,
                response_format=SynthesisResponse
            )
            logger.info("Successfully received response from LLM API")
            synthesis = response[0]
            
            # Return only the content, which is already in markdown format
            return synthesis.content
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            return "An error occurred while synthesizing the results."

def main(user_query: str, ranked_papers: RankedPapers):
    logger.info("Starting result synthesis...")
    synthesizer = ResultSynthesizer()
    synthesis = synthesizer.synthesize(ranked_papers, user_query)
    if synthesis:
        logger.info("Synthesis completed successfully.")
        print("Plan:")
        print(synthesis.plan)
        print("\nContent:")
        print(synthesis.content)
    else:
        logger.warning("Failed to generate a synthesis.")
    logger.info("Result synthesis completed.")

if __name__ == "__main__":
    # Example usage
    from models import RankedPaper
    
    logger.info("Starting example usage")
    # Simulating ranked papers with a variable number of papers
    example_results = RankedPapers(papers=[
        RankedPaper(
            id="1",
            title="Climate Change Impact on Water Resources",
            authors=["Smith, J.", "Johnson, A."],
            year=2021,
            doi="10.1234/water.2021.001",
            relevance_score=0.95,
            analysis="This paper discusses the direct effects of climate change on global water resources...",
            relevant_quotes=["Climate change is significantly altering the water cycle...", "Extreme weather events are becoming more frequent..."],
            bibtex="@article{smith2021climate, ...}"
        ),
        RankedPaper(
            id="2",
            title="Water Scarcity in a Changing Climate",
            authors=["Jones, B.", "Brown, C."],
            year=2020,
            doi="10.5678/climate.2020.002",
            relevance_score=0.92,
            analysis="The authors present a comprehensive review of water scarcity issues exacerbated by climate change...",
            relevant_quotes=["Water scarcity is projected to affect over 40% of the global population by 2050...", "Adaptation strategies are crucial for water resource management..."],
            bibtex="@article{jones2020water, ...}"
        ),
    ])
    logger.debug(f"Created example results with {len(example_results.papers)} papers")

    user_query = "How does climate change impact global water resources and what are potential management strategies?"
    logger.info(f"User query: {user_query}")
    main(user_query, example_results)
