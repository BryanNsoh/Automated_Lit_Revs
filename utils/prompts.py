import re

scopus_search_guide = """
Syntax and Operators

Valid syntax for advanced search queries includes:

Field codes (e.g. TITLE, ABS, KEY, AUTH, AFFIL) to restrict searches to specific parts of documents
Boolean operators (AND, OR, AND NOT) to combine search terms
Proximity operators (W/n, PRE/n) to find words within a specified distance - W/n: Finds terms within "n" words of each other, regardless of order. Example: journal W/15 publishing finds articles where "journal" and "publishing" are within two words of each other. - PRE/n: Finds terms in the specified order and within "n" words of each other. Example: data PRE/50 analysis finds articles where "data" appears before "analysis" within three words. - To find terms in the same sentence, use 15. To find terms in the same paragraph, use 50 -
Quotation marks for loose/approximate phrase searches
Braces {{}} for exact phrase searches
Wildcards (*) to capture variations of search terms
Invalid syntax includes:

Mixing different proximity operators (e.g. W/n and PRE/n) in the same expression
Using wildcards or proximity operators with exact phrase searches
Placing AND NOT before other Boolean operators
Using wildcards on their own without any search terms
Ideal Search Structure

An ideal advanced search query should:

Use field codes to focus the search on the most relevant parts of documents
Combine related concepts using AND and OR
Exclude irrelevant terms with AND NOT at the end
Employ quotation marks and braces appropriately for phrase searching
Include wildcards to capture variations of key terms (while avoiding mixing them with other operators)
Follow the proper order of precedence for operators
Complex searches should be built up systematically, with parentheses to group related expressions as needed. The information from the provided documents on syntax rules and operators should be applied rigorously.

** Critical: all double quotes other than the outermost ones should be preceded by a backslash (") to escape them in the JSON format. Failure to do so will result in an error when parsing the JSON string. **

Example Advanced Searches

{{
"query_1": "TITLE-ABS-KEY(("precision agriculture" OR "precision farming") AND ("machine learning" OR "AI") AND "water")",
"query_2": "TITLE-ABS-KEY((iot OR "internet of things") AND (irrigation OR watering) AND sensor*)",
"query_3": "TITLE-ABS-Key(("precision farming" OR "precision agriculture") AND ("deep learning" OR "neural networks") AND "water")",
"query_4": "TITLE-ABS-KEY((crop W/5 monitor*) AND "remote sensing" AND (irrigation OR water*))",
"query_5": "TITLE("precision irrigation" OR "variable rate irrigation" AND "machine learning")"
}}

** Critical: all double quotes other than the outermost ones should be preceded by a backslash (") to escape them in the JSON format. Failure to do so will result in an error when parsing the JSON string. **. 

These example searches demonstrate different ways to effectively combine key concepts related to precision agriculture, irrigation, real-time monitoring, IoT, machine learning and related topics using advanced search operators. They make use of field codes, Boolean and proximity operators, phrase searching, and wildcards to construct targeted, comprehensive searches to surface the most relevant research. The topic focus is achieved through carefully chosen search terms covering the desired themes.
"""

alex_search_guide = """
Syntax and Operators
Valid syntax for advanced alex search queries includes:
Using quotation marks %22%22 for exact phrase matches
Adding a minus sign - before terms to exclude them
Employing the OR operator in all caps to find pages containing either term
Using the site%3A operator to limit results to a specific website
Applying the filetype%3A operator to find specific file formats like PDF, DOC, etc.
Adding the * wildcard as a placeholder for unknown words
`
Invalid syntax includes:
Putting a plus sign + before words (alex stopped supporting this)
Using other special characters like %3F, %24, %26, %23, etc. within search terms
Explicitly using the AND operator (alex's default behavior makes it redundant)

Ideal Search Structure
An effective alex search query should:
Start with the most important search terms
Use specific, descriptive keywords related to irrigation scheduling, management, and precision irrigation
Utilize exact phrases in %22quotes%22 for specific word combinations
Exclude irrelevant terms using the - minus sign
Connect related terms or synonyms with OR
Apply the * wildcard strategically for flexibility
Note:

By following these guidelines and using proper URL encoding, you can construct effective and accurate search queries for alex.

Searches should be concise yet precise, following the syntax rules carefully. 

Example Searches
{{
"query_1": "https://api.openalex.org/works?search=%22precision+irrigation%22+%2B%22soil+moisture+sensors%22+%2B%22irrigation+scheduling%22&sort=relevance_score:desc&per-page=30",
"query_2": "https://api.openalex.org/works?search=%22machine+learning%22+%2B%22irrigation+management%22+%2B%22crop+water+demand+prediction%22&sort=relevance_score:desc&per-page=30",
"query_3": "https://api.openalex.org/works?search=%22IoT+sensors%22+%2B%22real-time%22+%2B%22soil+moisture+monitoring%22+%2B%22crop+water+stress%22&sort=relevance_score:desc&per-page=30",
"query_4": "https://api.openalex.org/works?search=%22remote+sensing%22+%2B%22vegetation+indices%22+%2B%22irrigation+scheduling%22&sort=relevance_score:desc&per-page=30",
"query_5": "https://api.openalex.org/works?search=%22wireless+sensor+networks%22+%2B%22precision+agriculture%22+%2B%22variable+rate+irrigation%22+%2B%22irrigation+automation%22&sort=relevance_score:desc&per-page=30"
}}

These example searches demonstrate how to create targeted, effective alex searches. They focus on specific topics, exclude irrelevant results, allow synonym flexibility, and limit to relevant domains when needed. The search terms are carefully selected to balance relevance and specificity while avoiding being overly restrictive.  By combining relevant keywords, exact phrases, and operators, these searches help generate high-quality results for the given topics.
"""


def remove_illegal_characters(text):
    if text is None:
        return ""
    illegal_chars = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")
    return illegal_chars.sub("", str(text))


def get_prompt(template_name, **kwargs):

    prompts = {
        "generate_queries": """
<documents>
<document index="1">
<source>search_query_prompt.txt</source>
<document_content>
<instructions>
Carefully review the provided context, including the specific point that needs to be addressed by the literature search, given in <point_content>. Your task is to generate a set of 10 highly optimized search queries that would surface the most relevant, insightful, and comprehensive set of research articles to shed light on various aspects of the particular point <point_content>. The queries should:
- Be thoughtfully crafted to return results that directly address the key issues and nuances of the <point_content>
- Demonstrate creativity and variety in their formulation to capture different dimensions of the topic
- Use precise terminology and logical operators to maintain a high signal-to-noise ratio in the results
- Cover a broad range of potential subtopics, perspectives, and article types related to the <point_content>
- Adhere strictly and diligently to any specific guidance or requirements provided in <search_guidance>. This is critical!
Provide your response strictly in the following JSON format as a single json object:
{{
    "query_1",
    "query_2", 
    "query_3",
    "query_4",
    "query_5",
    "query_6",
    "query_7",
    "query_8",
    "query_9",
    "query_10",  
}}
** Critical: all double quotes other than the outermost ones should be preceded by a backslash (\") to escape them in the JSON format. Failure to do so will result in an error when parsing the JSON string.
** The platform will be specified in the search guidance. Replace * with the platform name (e.g., scopus_queries, alex_queries). 
Each query_n should be replaced with a unique, well-formulated search entry according to the instructions in <search_guidance>. No other text should be included. Any extraneous text or deviation from this exact format will result in an unusable output.
</instructions>
<resources>
<point_content>
{point_content}
</point_content>
<search_guidance>
{search_guidance}
</search_guidance>
</resources>
</document_content>
</document>
</documents>
""",
        "rank_papers": """
<instructions>
First, carefully read through the full text of the paper provided under <full_text>. Then, analyze the paper's relevance to the specific point mentioned in <point_focus>.
Your analysis should include:
"verbatim_extracts": Provide the two most relevant verbatim quotes from the paper, each no more than 3 sentences, demonstrating its pertinence to the outline point and review. 
"explanation": A concise summary (3-5 sentences) of the key points of the paper as they relate to the outline point. Include this in the "explanation" field of the JSON.
"relevance_evaluation": A succinct yet detailed explanation of how the specifics of the paper contribute to addressing the point. Consider the following factors based on the paper type: relevance, insight, credibility, scope, and recency. Include this in the "relevance_evaluation" field of the JSON.
"relevance_score": A relevance score between 0 and 1 representing the overall fit of the paper to the point. Use the following rubric and include the score in the "relevance_score" field of the JSON:
0.0-0.19: Not relevant - Fails to address the point or provide any useful information. Should be excluded from the review.
0.2-0.39: Minimally relevant - Only briefly touches on the point with information that is of questionable value, reliability, or timeliness. Not recommended for inclusion.
0.4-0.49: Marginally relevant - Mostly tangential to the main issues of the point, with information of limited insight, credibility, or meaningfulness. Likely not essential.
0.5-0.59: Somewhat relevant - Addresses aspects of the point, but has significant limitations in scope, depth, reliability, or value of information. May still be worth including.
0.6-0.69: Moderately relevant - Provides useful information for the point, but has some notable gaps in addressing key issues or limitations in insight, credibility, or timeliness.
0.7-0.79: Very relevant - Directly informs the point with reliable and valuable information, but may have minor limitations in scope, depth, or recency.
0.8-0.89: Highly relevant - Addresses key issues of the point with novel, credible, and meaningful information. Adds substantial value to the review.
0.9-1.0: Exceptionally relevant - Comprehensively addresses all key aspects of the point with highly insightful, reliable, and up-to-date information. A must-include for the review.
Be uncompromising and extremely parsimonious in assigning the most appropriate score based on a holistic assessment of the paper's merits and limitations.
Default to a lower score if there are any doubts or reservations about the paper's relevance.

"limitations": List any important limitations of the paper for fully addressing the point and outline, such as limited scope, methodological issues, dated information, or tangential focus. If there are no major limitations, leave this blank. Include this in the "limitations" field of the JSON as a comma-separated list.
"inline_citation": Provide a suggested in-line citation for the paper under "inline_citation" in the format (Author, Year).
"apa_citation": Provide a full APA style reference under "apa_citation".
"study_location": Provide the specific city/region and country where the study was conducted. If not explicitly stated, infer the most likely location based on author affiliations or other context clues. If the location cannot be determined, write "Unspecified".
"main_objective": State the primary goal or research question of the study in 1-2 sentences.
"technologies_used": List the key technologies, methods, or approaches used in the study under "technologies_used", separated by commas.
"data_sources": List the primary sources of data used in the analysis, such as "Survey data", "Interviews", "Case studies", "Literature review", etc. Separate each source with a comma.
"key_findings": Summarize the main findings or results of the study in 2-3 sentences under "key_findings".

Provide your analysis in the following JSON format. Be as precise, specific, and concise as possible in your responses. Use the provided fields and format exactly as shown below:

<response_format>
{{
 "verbatim_extracts": ["Key terms and definitions", "Research questions or hypotheses", "Methodology descriptions", "Results, including statistics and data visualizations", "Tables and figures captions", "Quotes from participants or experts", "Author conclusions or summaries", "Limitations of the study or future research directions", "Include a long list of the most important text extracted verbatim from the provided paper", "Use quotes from the paper to support your summary"],
 "explanation": "From your close reading of the paper, provide a concise explanation of the study's purpose and main objectives, using a maximum of 3 sentences.",
 "relevance_evaluation": "Evaluate the relevance of the paper to the specific point being asked. Explain your reasoning in a maximum of 3 sentences.",
 "relevance_score": "On a scale from 0.0 to 1.0, parsimoniously rate the relevance of the paper to the point you are making in your review, with 1.0 being the most relevant.",
 "limitations": "List the main limitations of the study, separated by commas using a maximum of 2 sentences.",
 "inline_citation": "Provide the inline citation for the paper using the format: (Author Surname, Publication Year). If it's not directly provided, do your best to infer it",
 "apa_citation": "Provide the full APA citation for the paper, ensuring that all elements (author, year, title, publication, etc.) are correctly formatted. If it's not directly provided, do your best to infer it",
 "study_location": "Specify the city/region and country where the study was conducted.",
 "main_objective": "State the main objective of the study in 1-2 sentences.",
 "technologies_used": "List the key technologies used in the study, separated by commas. Be ultra-specific.",
 "data_sources": "List the main data sources used in the study, separated by commas. Be ultra-specific",
 "key_findings": "Summarize the key findings of the study in 2-3 sentences."
}}
</response_format>

Pay extreme attention to detail and include as much relevant information as possible within the specified constraints. Your analysis should be rigorous, insightful, and focused on the specific point provided in <point_focus>.
</instructions>

<context>

<point_focus>
{point_context}
</point_focus>

<full_text>
{full_text}
</full_text>

</context>
""",
        "synthesize_results": """
<prompt>
    <expert_description>
        You are a gifted polymath adept at synthesizing and breaking down rigorous research into digestible parts without sacrificing rigor, utilizing provided materials to offer a structured answer to the user's question through the synthesis of research papers.
    </expert_description>
    <user_query>
        {user_query}
    </user_query>
    <returned_results>
        {returned_results}
    </returned_results>
    <response_format>
        Structure your answer as a literature review section of a research paper, aimed at answering the user's question with data and insights from the provided returned_results. 
        Cite the research papers inline, including hyperlinks to the papers' DOI where necessary(you may need to add a https://doi.org/ to the DOI to make it a hyperlink). 
        Include full citations of the papers in the references section at the end. There will be no other sections other than the response and the references. 
        Organize the response in the way that feels most natural and clear.    </response_format>
</prompt>

""",
    }
    try:
        return prompts[template_name].format(**kwargs)

    except KeyError as e:
        missing_key = str(e).strip("'")
        raise ValueError(
            f"Missing argument for template '{template_name}': {missing_key}"
        )
