# analyze_papers.py
import asyncio
import json
import random
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from models import (
    Paper,
    RankedPaper,
    RankedPapers,
    SearchQueries,
    SearchResults,
    PaperAnalysis,
    SearchResult,
    RankingResponse,
    PaperRanking
)
from llm_api_handler import LLMAPIHandler
from logger_config import get_logger
import traceback

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

class PaperAnalyzer:
    def __init__(self):
        self.llm_api_handler = LLMAPIHandler()

    async def analyze_papers(self, search_results: SearchResults, claim: str) -> RankedPapers:
        papers = []
        for i, result in enumerate(search_results.results):
            paper = Paper(
                id=f"paper_{i}",
                doi=result.DOI,
                title=result.title,
                authors=result.authors,
                year=result.publication_year,
                full_text=result.full_text
            )
            papers.append(paper)

        logger.info(f"Analyzing {len(papers)} papers for claim: {claim}")
        ranked_papers = await self.rank_papers(papers, claim)
        return RankedPapers(papers=ranked_papers)

    async def rank_papers(self, papers: List[Paper], claim: str, num_rounds: int = 3, top_n: int = 5) -> List[RankedPaper]:
        logger.info(f"Starting to rank {len(papers)} papers")

        valid_papers = [paper for paper in papers if paper.full_text and len(paper.full_text.split()) >= 200]
        logger.info(f"After filtering, {len(valid_papers)} valid papers remain")
        
        if not valid_papers:
            logger.warning("No valid papers to rank. Returning empty list.")
            return []
        
        paper_scores: Dict[str, List[float]] = {paper.id: [] for paper in valid_papers}
        
        all_prompts = []

        for round in range(num_rounds):
            logger.info(f"Starting ranking round {round + 1} of {num_rounds}")
            shuffled_papers = random.sample(valid_papers, len(valid_papers))
            
            paper_groups = create_balanced_groups(shuffled_papers)
            
            for group in paper_groups:
                paper_summaries = "\n".join([
                    f"Paper ID: {paper.id}\n"
                    f"Title: {paper.title}"
                    for paper in group
                ])
                prompt = RANKING_PROMPT.format(claim=claim, paper_summaries=paper_summaries, num_papers=len(group))
                all_prompts.append((group, prompt))

        prompts = [prompt for group, prompt in all_prompts]
        logger.debug(f"Sending {len(prompts)} prompts for batch ranking")
        try:
            rankings_responses = await self.llm_api_handler.async_process(
                prompts=prompts,
                model="gpt-4o-mini",
                system_message="You are a helpful assistant tasked with ranking research papers.",
                temperature=0.6,
                response_format=RankingResponse
            )
            logger.debug(f"Received {len(rankings_responses)} ranking responses")
        except Exception as e:
            logger.error(f"Batch ranking failed: {str(e)}")
            logger.error(traceback.format_exc())
            return []
        
        for (group, prompt), ranking_response in zip(all_prompts, rankings_responses):
            logger.debug(f"Processing rankings for group of {len(group)} papers")
            logger.debug(f"Rankings received: {ranking_response}")
            
            if not isinstance(ranking_response, RankingResponse):
                logger.warning(f"Unexpected ranking response format. Expected RankingResponse, got: {type(ranking_response)}")
                continue
            
            for ranking in ranking_response.rankings:
                paper_id = ranking.paper_id
                rank = ranking.rank
                group_size = len(group)
                if group_size > 0:
                    score = (group_size - rank + 1) / group_size
                else:
                    score = 0
                
                if paper_id not in paper_scores:
                    logger.warning(f"Unexpected paper_id received: {paper_id}. Expected one of: {list(paper_scores.keys())}")
                    continue
                
                paper_scores[paper_id].append(score)
                logger.debug(f"Paper {paper_id} ranked {rank}/{group_size}, score: {score}")
        
        average_scores = {paper_id: sum(scores) / len(scores) if scores else 0 for paper_id, scores in paper_scores.items()}
        
        sorted_papers = sorted(valid_papers, key=lambda p: average_scores[p.id], reverse=True)
        
        logger.info("\nScores of all papers:")
        for paper in sorted_papers:
            logger.info(f"Paper ID: {paper.id}, Title: {paper.title}, Average Score: {average_scores[paper.id]:.2f}")

        top_papers = sorted_papers[:top_n]
        analysis_tasks = [self.analyze_paper(claim, paper) for paper in top_papers]
        paper_analyses = await asyncio.gather(*analysis_tasks)
        
        ranked_papers = []
        for paper, analysis in zip(top_papers, paper_analyses):
            ranked_paper = RankedPaper(
                id=paper.id,
                doi=paper.doi,
                title=paper.title,
                authors=paper.authors,
                year=paper.year,
                relevance_score=average_scores[paper.id],
                analysis=analysis.analysis,
                relevant_quotes=analysis.relevant_quotes
            )
            ranked_papers.append(ranked_paper)
        
        logger.info(f"Completed paper ranking. Top score: {ranked_papers[0].relevance_score:.2f}, Bottom score: {ranked_papers[-1].relevance_score:.2f}")
        return ranked_papers

    async def analyze_paper(self, claim: str, paper: Paper) -> PaperAnalysis:
        prompt = ANALYSIS_PROMPT.format(
            claim=claim,
            full_text=paper.full_text,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            doi=paper.doi,
        )
        
        logger.debug(f"Analyzing paper: {paper.title}")
        logger.debug(f"Analysis prompt: {prompt[:100]}...")
        
        try:
            analysis_response = await self.llm_api_handler.async_process(
                prompts=[prompt],
                model="gpt-4o-mini",
                system_message="You are a helpful assistant tasked with analyzing research papers.",
                temperature=0.6,
                response_format=PaperAnalysis   
            )
            analysis = analysis_response[0]
            logger.debug(f"Paper Analysis: {analysis}")
            
            if isinstance(analysis, dict):
                analysis = PaperAnalysis(**analysis)
            elif not isinstance(analysis, PaperAnalysis):
                logger.warning(f"Unexpected analysis type: {type(analysis)}")
                raise ValueError(f"Unexpected analysis type: {type(analysis)}")
            
            return analysis
        except Exception as e:
            logger.error(f"Error during paper analysis: {str(e)}")
            logger.error(traceback.format_exc())
            return PaperAnalysis(analysis="", relevant_quotes=[])

async def main(search_queries: SearchQueries, search_results: SearchResults, claim: str, top_n: int = 5):
    analyzer = PaperAnalyzer()
    analysis_results = await analyzer.analyze_papers(search_results, claim)
    return analysis_results