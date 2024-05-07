import re

scopus_search_guide = """
Syntax and Operators

Valid syntax for advanced search queries includes:

Field codes (e.g. TITLE, ABS, KEY, AUTH, AFFIL) to restrict searches to specific parts of documents
Boolean operators (AND, OR, AND NOT) to combine search terms
Proximity operators (W/n, PRE/n) to find words within a specified distance - W/n: Finds terms within "n" words of each other, regardless of order. Example: journal W/15 publishing finds articles where "journal" and "publishing" are within two words of each other. - PRE/n: Finds terms in the specified order and within "n" words of each other. Example: data PRE/50 analysis finds articles where "data" appears before "analysis" within three words. - To find terms in the same sentence, use 15. To find terms in the same paragraph, use 50 -
Quotation marks for loose/approximate phrase searches
Braces {{}} for exact phrase searches (without hte backslashes of course)
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

core_search_guide = """
### CORE API Search Guide: Formulating Queries in JSON Format

This guide provides a structured approach to creating effective search queries using the CORE API. The guide emphasizes the JSON format to ensure clarity and precision in your search queries.

#### Syntax and Operators

**Valid Syntax for CORE API Queries:**
- **Field-specific searches**: Direct your query to search within specific fields like `title`, `author`, or `subject`.
- **Boolean Operators**: Use `AND`, `OR`, and `NOT` to combine or exclude terms.
- **Grouping**: Use parentheses `()` to structure the query and define the order of operations.
- **Range Queries**: Specify ranges for dates or numerical values with `>`, `<`, `>=`, `<=`.
- **Existence Check**: Use `_exists_` to filter results based on the presence of data in specified fields.

**Invalid Syntax:**
- **Inconsistencies in field names**: Ensure field names are correctly spelled and appropriate for the data type.
- **Improper boolean logic**: Avoid illogical combinations that nullify the search criteria (e.g., `AND NOT` used incorrectly).

#### Ideal Query Structure

Your search queries should:
1. **Use Field-Specific Filters**: Focus your search on the most relevant attributes.
2. **Combine Keywords Effectively**: Use logical operators to refine and broaden your searches.
3. **Employ Grouping and Range Queries** where complex relationships or specific time frames are needed.

#### Example Advanced Searches in JSON Format

Here are examples of structured queries formatted in JSON, demonstrating different ways to effectively combine search criteria using the CORE API:

```json
{
    "query_1": {
        "search_query": "climate change, water resources",
        "query_rationale": "This query is essential to understand the overall impact of climate change on global water resources, providing a broad understanding of the topic.",
    },
    "query_2": {
        "search_query": "water scarcity, (hydrologist OR water expert)",
        "query_rationale": "This query is necessary to identify areas with high water scarcity and how climate change affects the global distribution of water resources.",
    },
    "query_3": {
        "search_query": "sea level rise, coastal erosion",
        "query_rationale": "This query is crucial to understand the impact of climate change on coastal regions and the resulting effects on global water resources.",
    },
    "query_4": {
        "search_query": "water conservation, climate change mitigation, environmental studies",
        "query_rationale": "This query is important to identify strategies for water conservation and their role in mitigating the effects of climate change on global water resources.",
    },
    "query_5": {
        "search_query": "glacier melting, cryosphere",
        "query_rationale": "This query is necessary to understand the impact of climate change on glaciers and the resulting effects on global water resources.",
    },
}
```

### Critical Considerations

- **Escape Characters**: When using JSON format, ensure that all double quotes inside JSON values are properly escaped using backslashes (`\"`) to prevent parsing errors.
- **Complexity**: As queries become more complex, ensure they are still readable and maintainable. Use whitespace and indentation in JSON to enhance clarity.

These examples illustrate how to utilize the CORE API's flexible query capabilities to target specific fields, combine search terms logically, and exclude irrelevant data. By following these guidelines and adapting the examples to your research needs, you can efficiently leverage the CORE API to access a vast range of academic materials.
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
Review the user's main query: '{user_query}'. Break down this query into distinct sub-queries that address different aspects necessary to fully answer the main query. 
For each sub-query, provide a rationale explaining why it is essential. Format these sub-queries according to the directions in <search_guidance>. structure your response as a json with detailed search queries, each accompanied by its rationale. 
The output should adhere to this format:
{{
  "query_1": {{
    "search_query": "unique query following the provided search guidance",
    "query_rationale": "This query is essential to understand the overall impact of climate change on global water resources, providing a broad understanding of the topic."
  }},
  "query_2": {{
    "search_query": "unique query following the provided search guidance",
    "query_rationale": "This query is necessary to identify areas with high water scarcity and how climate change affects the global distribution of water resources."
  }},
  ...
}}
**Note: Only generate as many sub-queries and rationales as necessary to thoroughly address the main query, up to a maximum of 10. Each sub-query must directly contribute to unraveling the main query's aspects.
</instructions>
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
Analyze the paper's relevance to {point_context} from the {query_rationale} perspective. 

Begin your response with the relevance score between the following tokens:
<<relevance>>*.*<<relevance>>
The relevance score should be a decimal between 0.0 and 1.0, with 1.0 being the most relevant. If there is not enough information to determine relevance, assign a score of 0.0.
Examples:
- Correct: "<<relevance>>0.9<<relevance>>"
- Correct: "<<relevance>>0.3<<relevance>>"
- Correct: "<<relevance>>0.0<<relevance>>"
After providing the relevance score, include the following in your analysis:

Include in your analysis:
- Verbatim extracts: key terms, research questions, methods, results, tables, figures, quotes, conclusions
- Explanation of study purpose and objectives
- Relevance evaluation to the specified point
- Limitations for addressing the point
- Free-form extraction with relevant verbatim information (any format). Extract as much verbatim information as needed to support your analysis.

End with this JSON:
<response_format>
{{
  "inline_citation": "<author surname>, <year>",
  "apa_citation": "<full APA citation>",
  "study_location": "<city/region, country>", 
  "main_objective": "<main objective>",
  "technologies_used": "<technology 1>, <technology 2>, ...",
  "data_sources": "<data source 1>, <data source 2>, ...",
  "key_findings": "<key findings summary>"
}}
</response_format>
</instructions>

<full_text>
{full_text}
</full_text>
""",
        "synthesize_results": """
<prompt>
    <expert_description>
        You are an expert polymath skilled in deep analysis and synthesis of complex research information. Utilize the provided materials, as well as any other relevant data, facts, or discussions provided to you, to construct a detailed and technically rigorous response that is akin to a high-level research analysis. Include all pertinent data, facts, and figures that aid in constructing a comprehensive analysis. Your response should reflect the depth of understanding expected from a seasoned researcher or PhD holder, ensuring no details are overlooked.
    </expert_description>
    <user_query>
        {user_query}
    </user_query>
    <returned_results>
        {returned_results}
    </returned_results>
    <response_format>
        Provide a comprehensive, structured response that rigorously analyzes and interprets the data and insights from the provided research materials and any other relevant information you have been provided with. 
        Mention any pertinent data, facts, numbers, etc., ensuring they are properly attributed. Cite the research papers inline, including hyperlinks to the papers' DOI where necessary (you may need prepend with https://doi.org/ to make it a hyperlink). e.g [author et al 2021](). 
        Conclude with a full citation of all referenced papers. Structure your response in a clear, logical manner, focusing on technical accuracy and depth to thoroughly answer the user's query based on the provided data. 
        Keep your answer tightly focused on the user's query and only include relevant/pertinent information. Begin you answer without preamble.
    </response_format>
    <critical-points>
        - Only include and discuss sources that are directly relevant to the user query.
        - Sources which are not directly relevant to the user query should not be included in the response.
    </critical-points>
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
