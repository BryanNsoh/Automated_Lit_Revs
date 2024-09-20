import asyncio
import logging
from llm_api_handler import LLMAPIHandler
from models import RankedPapers, RankedPaper
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYNTHESIS_PROMPT = """
Analyze and synthesize the findings from the following papers related to the query: "{user_query}"

{paper_details}

Please provide a comprehensive analysis based on these findings. Your response should:
1. Summarize the main points from each paper.
2. Identify common themes or contradictions across the papers.
3. Discuss how these findings address the original query.
4. Highlight any limitations or areas for further research.

Format your response in markdown, using appropriate headers, bullet points, and emphasis where necessary. Cite the papers using [1], [2], [3], etc. corresponding to the order they are presented above.

Your response should be detailed, academic in tone, and approximately 1000 words long.
"""

class ResultSynthesizer:
    def __init__(self):
        self.llm_api_handler = LLMAPIHandler()

    def _format_quotes(self, quotes: List[str]) -> str:
        return "\n".join([f"- {quote}" for quote in quotes])

    def _format_paper_details(self, papers):
        paper_details = ""
        for i, paper in enumerate(papers, 1):
            paper_details += f"""
Paper {i}:
Title: {paper.paper.title}
Analysis: {paper.analysis}
Relevant Quotes:
{self._format_quotes(paper.relevant_quotes)}

"""
        return paper_details.strip()

    async def synthesize_results(self, user_query: str, ranked_papers: RankedPapers) -> str:
        papers = ranked_papers.papers  # Use all available papers

        paper_details = self._format_paper_details(papers)

        prompt = SYNTHESIS_PROMPT.format(
            user_query=user_query,
            paper_details=paper_details
        )

        try:
            logger.info(f"Synthesizing results for query: {user_query}")
            response = await self.llm_api_handler.process(
                prompts=[prompt],
                model="gpt-4o-mini",
                mode="async",
                response_format=str
            )
            logger.info("Successfully received response from LLM API")
            return response[0]  # Return the first (and only) response
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            return None

async def main(user_query: str, ranked_papers: RankedPapers):
    synthesizer = ResultSynthesizer()
    logger.info("Starting result synthesis...")
    synthesis = await synthesizer.synthesize_results(user_query, ranked_papers)
    if synthesis:
        logger.info("Synthesis completed successfully.")
        print(synthesis)  # This will be the markdown-formatted text
    else:
        logger.warning("Failed to generate a synthesis.")
    logger.info("Result synthesis completed.")

if __name__ == "__main__":
    # Example usage
    from models import RankedPaper, Paper
    
    # Simulating ranked papers with a variable number of papers
    example_results = RankedPapers(papers=[
        RankedPaper(
            id="1",
            title="Climate Change Impact on Water Resources",
            relevance_score=0.95,
            analysis="This paper discusses the direct effects of climate change on global water resources...",
            relevant_quotes=["Climate change is significantly altering the water cycle...", "Extreme weather events are becoming more frequent..."],
            bibtex="@article{smith2021climate, ...}"
        ),
        RankedPaper(
            id="2",
            title="Water Scarcity in a Changing Climate",
            relevance_score=0.92,
            analysis="The authors present a comprehensive review of water scarcity issues exacerbated by climate change...",
            relevant_quotes=["Water scarcity is projected to affect over 40% of the global population by 2050...", "Adaptation strategies are crucial for water resource management..."],
            bibtex="@article{jones2020water, ...}"
        ),
        # Uncomment the following to test with more or fewer papers
        # RankedPaper(
        #     id="3",
        #     title="Sustainable Water Management Under Climate Uncertainty",
        #     relevance_score=0.88,
        #     analysis="This study proposes innovative approaches to water management in the face of climate uncertainty...",
        #     relevant_quotes=["Integrated water resource management is key to addressing climate change impacts...", "Nature-based solutions show promise in enhancing water security..."],
        #     bibtex="@article{zhang2022sustainable, ...}"
        # ),
    ])

    user_query = "How does climate change impact global water resources and what are potential management strategies?"
    asyncio.run(main(user_query, example_results))
