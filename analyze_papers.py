import asyncio
import json
import random
from typing import List, Dict
from pydantic import BaseModel, Field
from models import (
    Paper,
    RankedPaper,
    RankedPapers,
    SearchQueries,
    SearchResults,
    PaperAnalysis,
    SearchResult
)
from llm_api_handler import LLMAPIHandler
from utils.bibtex import get_bibtex_from_doi, get_bibtex_from_title
from logger_config import get_logger

logger = get_logger(__name__)

RANKING_PROMPT = """
Analyze the relevance of the following papers to the query: "{claim}"

Papers:
{paper_summaries}

Rank these papers from most to least relevant based on the following criteria:
1. Direct relevance to the claim (either supporting or refuting it)
2. Quality and reliability of the research
3. Recency and impact of the findings
4. Presence of relevant information. If methods or results section are not present in full detail, the paper cannot be considered evaluative of the claim and should be ranked lower.

Focus primarily on the full text content of each paper. Other metadata (title, authors, etc.) may be missing or incomplete, but should not significantly affect your ranking if the full text is present.

Your response should be in the following JSON format:
{{
  "rankings": [
    {{
      "paper_id": "string",
      "rank": integer,
      "explanation": "string"
    }},
    ...
  ]
}}

Ensure that each paper is assigned a unique rank from 1 to {num_papers}, where 1 is the most relevant. Provide a concise, technical explanation for each ranking, focusing on how the paper's content directly addresses the claim.
"""

ANALYSIS_PROMPT = """
Provide a super detailed, ultra technical analysis of the following paper's relevance to the query: "{claim}"

Paper Details:
Title: {title}
Authors: {authors}
Publication Year: {year}
DOI: {doi}
Abstract: {abstract}
Full Text: {full_text}

Your response must be in the following JSON format:
{{
  "analysis": "string, 500 words minimum",
  "relevant_quotes": [
    "string, 100 words minimum. Really extract a big chunk of what you think is the crux of the paper",
    "string, 100 words minimum. Really extract a big chunk of what you think is the crux of the paper",
    "string, 100 words minimum. Really extract a big chunk of what you think is the crux of the paper"
  ]
}}

In the analysis:
1. Evaluate how directly the paper addresses the claim, either supporting or refuting it.
2. Assess the methodology, sample size, and statistical significance of the findings if relevant.
3. Consider any limitations or potential biases in the study.
4. Discuss how the paper's findings contribute to the broader understanding of the claim. Devote most of your time to this.

Extract exactly three relevant quotes from the paper that best support your analysis. These should be verbatim excerpts that directly relate to the claim.

Ensure your analysis is highly precise, technical, and grounded in the paper's content. Avoid general statements and focus on ultra specific details from the methods, results, and discussion sections.
"""

def create_balanced_groups(papers: List[Paper], min_group_size: int = 2, max_group_size: int = 5) -> List[List[Paper]]:
    num_papers = len(papers)
    logger.info(f"Creating balanced groups for {num_papers} papers")
    logger.info(f"min_group_size: {min_group_size}, max_group_size: {max_group_size}")

    if num_papers < min_group_size:
        logger.warning(f"Too few papers ({num_papers}) to create groups. Returning single group.")
        return [papers]

    try:
        if num_papers < max_group_size:
            logger.info(f"Number of papers ({num_papers}) less than max_group_size ({max_group_size}). Using num_papers as group size.")
            group_size = num_papers
        else:
            inner_division = num_papers // max_group_size
            logger.info(f"Inner division result: {inner_division}")
            if inner_division == 0:
                logger.warning(f"Inner division resulted in zero. Using max_group_size ({max_group_size}) as group size.")
                group_size = max_group_size
            else:
                group_size = min(max_group_size, max(min_group_size, num_papers // inner_division))
        
        logger.info(f"Calculated group size: {group_size}")

        groups = [papers[i:i+group_size] for i in range(0, num_papers, group_size)]
        
        if len(groups[-1]) < min_group_size:
            last_group = groups.pop()
            for i, paper in enumerate(last_group):
                groups[i % len(groups)].append(paper)
        
        logger.info(f"Created {len(groups)} groups")
        return groups

    except Exception as e:
        logger.error(f"Error in create_balanced_groups: {str(e)}")
        logger.error(f"Falling back to single group")
        return [papers]

async def retry_llm_query(handler: LLMAPIHandler, prompt: str, model: str, max_retries: int = 3) -> Dict[str, any]:
    for attempt in range(max_retries):
        try:
            response = await handler.process(
                prompts=[prompt],
                model=model,
                mode="async",
                response_format=dict
            )
            return response[0]
        except json.JSONDecodeError:
            logger.warning(f"Attempt {attempt + 1}/{max_retries}: Failed to parse LLM response as JSON.")
            if attempt == max_retries - 1:
                logger.error(f"All attempts failed. Last response: {response}")
                raise ValueError("Failed to get valid JSON response after multiple attempts")
        except Exception as e:
            logger.error(f"Error during LLM query: {str(e)}")
            raise

async def rank_group(handler: LLMAPIHandler, claim: str, papers: List[Paper]) -> List[Dict[str, any]]:
    paper_summaries = "\n".join([
        f"Paper ID: {paper.id}\n"
        f"Full Text: {getattr(paper, 'full_text', 'N/A')[:500]}...\n"
        f"Title: {getattr(paper, 'title', 'N/A')}\n"
        f"Abstract: {getattr(paper, 'abstract', 'N/A')[:200]}..."
        for paper in papers
    ])
    prompt = RANKING_PROMPT.format(claim=claim, paper_summaries=paper_summaries, num_papers=len(papers))
    
    try:
        rankings = await retry_llm_query(handler, prompt, model="gpt-4o-mini")
        print(f"Group Rankings: {rankings}")
        
        if isinstance(rankings, dict) and "rankings" in rankings:
            rankings = rankings["rankings"]
        
        if not isinstance(rankings, list) or len(rankings) != len(papers):
            logger.warning(f"Unexpected rankings format. Expected list of {len(papers)} items, got: {rankings}")
            raise ValueError("Unexpected rankings format")
        
        return rankings
    except Exception as e:
        logger.error(f"Error during ranking: {str(e)}")
        return []

async def analyze_paper(handler: LLMAPIHandler, claim: str, paper: Paper) -> Dict[str, any]:
    prompt = ANALYSIS_PROMPT.format(
        claim=claim,
        full_text=getattr(paper, 'full_text', 'N/A'),
        title=getattr(paper, 'title', 'N/A'),
        authors=getattr(paper, 'authors', 'N/A'),
        year=getattr(paper, 'year', 'N/A'),
        doi=getattr(paper, 'doi', 'N/A'),
        abstract=getattr(paper, 'abstract', 'N/A')
    )
    
    try:
        analysis = await retry_llm_query(handler, prompt, model="gpt-4o-mini")
        print(f"Paper Analysis: {analysis}")
        
        if not isinstance(analysis, dict) or 'analysis' not in analysis or 'relevant_quotes' not in analysis:
            logger.warning("Incomplete analysis received")
            raise ValueError("Incomplete analysis received")
        
        return analysis
    except Exception as e:
        logger.error(f"Error during paper analysis: {str(e)}")
        return {"analysis": "", "relevant_quotes": []}

class PaperAnalyzer:
    def __init__(self):
        self.llm_api_handler = LLMAPIHandler()

    async def rank_papers(self, papers: List[Paper], claim: str, num_rounds: int = 7, top_n: int = 5) -> List[RankedPaper]:
        logger.info(f"Starting to rank {len(papers)} papers")

        valid_papers = [paper for paper in papers if getattr(paper, 'full_text', '') and len(getattr(paper, 'full_text', '').split()) >= 200]
        logger.info(f"After filtering, {len(valid_papers)} valid papers remain")
        
        unique_papers = []
        seen_dois = set()
        seen_titles = set()
        for paper in valid_papers:
            if getattr(paper, 'doi', None) and paper.doi not in seen_dois:
                seen_dois.add(paper.doi)
                unique_papers.append(paper)
            elif getattr(paper, 'title', None) and paper.title not in seen_titles:
                seen_titles.add(paper.title)
                unique_papers.append(paper)
        
        for i, paper in enumerate(unique_papers):
            if not hasattr(paper, 'id'):
                setattr(paper, 'id', f"paper_{i}")
        
        paper_scores: Dict[str, List[float]] = {paper.id: [] for paper in unique_papers}
        
        for round in range(num_rounds):
            logger.info(f"Starting ranking round {round + 1} of {num_rounds}")
            shuffled_papers = random.sample(unique_papers, len(unique_papers))
            
            paper_groups = create_balanced_groups(shuffled_papers)
            
            ranking_tasks = [rank_group(self.llm_api_handler, claim, group) for group in paper_groups]
            group_rankings = await asyncio.gather(*ranking_tasks)
            
            for rankings in group_rankings:
                group_size = len(rankings)
                for ranking in rankings:
                    paper_id = ranking['paper_id']
                    rank = ranking['rank']
                    score = (group_size - rank + 1) / group_size
                    paper_scores[paper_id].append(score)
        
        average_scores = {}
        for paper_id, scores in paper_scores.items():
            if scores:
                average_scores[paper_id] = sum(scores) / len(scores)
            else:
                logger.warning(f"No scores recorded for paper {paper_id}. Assigning lowest score.")
                average_scores[paper_id] = 0
        
        sorted_papers = sorted(unique_papers, key=lambda p: average_scores[p.id], reverse=True)
        
        print("\nScores of all papers:")
        for paper in sorted_papers:
            print(f"Paper ID: {paper.id}, Title: {paper.title}, Average Score: {average_scores[paper.id]:.2f}")

        top_papers = sorted_papers[:top_n]
        analysis_tasks = [analyze_paper(self.llm_api_handler, claim, paper) for paper in top_papers]
        paper_analyses = await asyncio.gather(*analysis_tasks)
        
        ranked_papers = []
        for paper, analysis in zip(top_papers, paper_analyses):
            paper_dict = paper.__dict__.copy()
            paper_dict.pop('id', None)
            ranked_paper = RankedPaper(
                **paper_dict,
                relevance_score=average_scores[paper.id],
                analysis=analysis['analysis'],
                relevant_quotes=analysis['relevant_quotes']
            )
            bibtex = get_bibtex_from_doi(ranked_paper.doi) if ranked_paper.doi else None
            if not bibtex:
                bibtex = get_bibtex_from_title(ranked_paper.title, ranked_paper.authors, ranked_paper.year)
            ranked_paper.bibtex = bibtex or ""
            ranked_papers.append(ranked_paper)
        
        logger.info(f"Completed paper ranking. Top score: {ranked_papers[0].relevance_score:.2f}, Bottom score: {ranked_papers[-1].relevance_score:.2f}")
        return ranked_papers

    async def analyze_papers(self, search_results: SearchResults, claim: str) -> RankedPapers:
        papers = []
        for result in search_results.results.values():
            paper = Paper(
                doi=result.DOI,
                title=result.title,
                authors=result.authors,
                year=result.publication_year,
                abstract=result.abstract,
                full_text=result.full_text
            )
            papers.append(paper)

        ranked_papers = await self.rank_papers(papers, claim)
        return RankedPapers(papers=ranked_papers)

async def main(search_queries: SearchQueries, search_results: SearchResults, claim: str, top_n: int = 5):
    analyzer = PaperAnalyzer()
    analysis_results = await analyzer.analyze_papers(search_results, claim)
    return analysis_results

if __name__ == "__main__":
    # Example usage
    from core_search import CORESearch, SearchQuery

    async def run_example():
        # Simulate search queries and results
        search_queries = SearchQueries(queries={
            "query_1": SearchQuery(
                search_query="climate change, water resources",
                query_rationale="This query is essential to understand the overall impact of climate change on global water resources."
            ),
            "query_2": SearchQuery(
                search_query="water scarcity, (hydrologist OR water expert)",
                query_rationale="This query is necessary to identify areas with high water scarcity."
            )
        })

        core_search = CORESearch(max_results=5)
        search_results = await core_search.search_and_parse_queries(search_queries)

        claim = "Climate change significantly impacts global water resources."
        analysis_results = await main(search_queries, search_results, claim)

        print(analysis_results.json(indent=2))

    asyncio.run(run_example())
