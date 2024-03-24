import re


outline = """ 
A systematic review of automated systems for real-time irrigation management

1. INTRODUCTION
1.1	The Global Food Challenge and the Role of Irrigation
•	The challenge of feeding a growing population with finite resources
•	The role and importance of irrigation in enhancing crop yields and agricultural productivity
•	The necessity of scalable water-efficient practices for increasing food demand
1.2. Traditional Irrigation: Limitations and the Need for Automation
•	Definition of irrigation scheduling and management
•	Historical irrigation management techniques (e.g., manual and timer-based scheduling)
•	Limitations: labor-intensive, inefficient water use, less adaptable to changing conditions
•	Need for scalable, automated solutions for greater efficiency
1.3. The Emergence of Smart Irrigation Management and IoT
•	Contrast between modern and historical irrigation management, emphasizing automation
•	Technologies for smart irrigation management (e.g., remote sensing, sensor networks, weather data, and computational algorithms)
•	Key point: modern approaches rely on vast data and analysis algorithms
•	The role of IoT in collecting vast amounts of data through sensors, data transmission, and tailored networks
•	The importance of real-time data for dynamic irrigation systems and automated management at a larger scale
•	Challenges hampering the full benefit of IoT: processing diverse data sources, data integration, and lack of integrated data analysis
1.4. Machine Learning and Real-time/Automated Systems in Irrigation Management
•	Machine learning (ML) in processing vast data, predicting plant stress, modeling climate effects, and optimizing irrigation
•	ML's potential constrained by manual steps (data interpretation, decision-making on irrigation timing and volume, and system adjustments)
•	The need for automating ML integration to allow direct action from insights to irrigation execution, removing bottlenecks and achieving real-time adaptability
•	The current fragmented approach in smart irrigation due to focusing on pieces rather than the entire picture
•	The need for automating and integrating each section of the irrigation management pipeline for autonomous real-time end-to-end irrigation management
•	Full autonomous irrigation management pipeline: sensor/weather data -> transmission -> processing/analysis -> algorithmic decision-making -> automated action
•	Benefits of automation: easing bottlenecks in data collection, insight generation, and processing; freeing up labor and fostering scalability
1.5 Interoperability and Standardization: Key Enablers for Seamless Integration
•	The critical role of interoperability and standardization in enabling seamless integration across the automated irrigation management system
•	Challenges of integrating heterogeneous data sources, devices, and systems
•	Standardized protocols and data formats as essential for achieving seamless integration and ensuring compatibility between components
•	Existing and emerging standards (e.g., OGC SensorThings API, ISO 11783) and their applicability to real-time irrigation management systems
•	1.6. Objectives of the Review
•	Primary Objective: To critically evaluate the current state and future potential of real-time, end-to-end automated irrigation management systems that integrate IoT and machine learning technologies for enhancing agricultural water use efficiency and crop productivity.
•	Specific Objective 1: Examining the automation of each part of the irrigation management pipeline and the seamless integration of each section in the context of irrigation scheduling and management.
•	Specific Objective 2: Analyze the effectiveness and efficiency of integrated end-to-end automated irrigation systems
•	Specific Objective 3: Investigate the role of interoperability and standardization in enabling the integration of components within the automated irrigation management pipeline
•	Specific Objective 4: Identify gaps and propose solutions for seamless integration across the automated irrigation management system, aiming to achieve fully autonomous, scalable irrigation management.

2. REVIEW METHODOLOGY
•	Question-driven framework to guide the literature review of real-time, autonomous irrigation management systems
•	Key research questions posed, each with the motivation behind investigating them and a starting hypothesis to evaluate against the examined literature
•	Table presenting the major objectives, specific objectives, questions, motivations, and hypotheses
3. DATA COLLECTION TO CLOUD: AUTOMATION AND REAL-TIME PROCESSING
3.1. Irrigation management data
•	Types of data most applicable to irrigation management and their typical sources
•	Different data types (e.g., soil moisture, canopy temperature, weather) and their collection and use
•	Considerations: volume, frequency, format, and source of the data
3.2. Edge Computing and Fog Computing
•	The potential of edge computing and fog computing in real-time irrigation management
•	Benefits of edge computing in reducing latency, enabling real-time decision-making, and reducing reliance on cloud connectivity
•	The role of fog computing in distributing processing and storage across the network, enhancing scalability and reliability
3.3. Automation of Data Collection
3.4. Real-Time Data Transmission Protocols and Technologies
•	Exploration of MQTT and client-server IoT networks for real-time data transmission
•	Comparison of application layer protocols (e.g., XMPP, CoAP, SOAP, HTTP) and their suitability for real-time irrigation management
3.5. Challenges and Solutions in Real-Time Data Transmission
•	Obstacles in transmitting data in real-time
•	Solutions implemented to address these challenges
3.6. IoT Network Architectures and Variable Rate Irrigation (VRI) for Real-Time Irrigation
•	Strategies for collecting and managing VRI data at scale
•	Autonomous planning and scheduling of VRI using machine learning and optimization techniques
•	Challenges and solutions for implementing VRI in real-time, end-to-end automated irrigation systems
4. AUTOMATED DATA PROCESSING IN THE CLOUD
4.1. Data Quality and Preprocessing
•	The importance of data quality and preprocessing in the automated irrigation management pipeline
•	Techniques for data cleaning, outlier detection, and handling missing or inconsistent data in real-time
•	The impact of data quality on the accuracy and reliability of ML models and decision-making processes
4.2. Containerization Strategies for Scalable and Autonomous Deployment
•	Examination of containerization technologies (e.g., Docker, Kubernetes) for hosting, running, and scaling ML/data processing modules in the cloud
•	Benefits and challenges of containerization in the context of real-time irrigation management
•	Scalability and performance optimization techniques, such as parallel processing, distributed computing, and resource allocation strategies
4.3. Deploying ML Models for Data Processing
•	Details on the deployment of ML models on cloud platforms for real-time data processing and inference
4.4. Online Learning in the Cloud
•	Investigation of the use of online learning models for continuous improvement based on incoming data


5. GENERATING AND APPLYING IRRIGATION INSIGHTS 
5.1. Real-Time Generation of Insights
•	Examination of the application of predictive models in generating actionable irrigation insights in real-time
5.2. Automated Application of Insights
•	Exploration of strategies for the automated application of ML-generated insights to control irrigation systems without manual intervention
5.3. Interpretability and Explainability of ML Models
•	The importance of interpretability and explainability in ML models used for irrigation management
•	Techniques for enhancing the transparency and interpretability of ML models, enabling users to understand and trust the generated insights and decisions
•	The role of explainable AI (XAI) in building user confidence and facilitating human-machine collaboration in automated irrigation systems

6. INTEGRATION, INTEROPERABILITY, AND STANDARDIZATION 
6.1. Interoperability and Standardization
6.2. Integration with Existing Irrigation Infrastructure
•	Challenges and strategies for integrating automated systems with existing irrigation infrastructure
•	Compatibility issues and retrofit solutions for incorporating IoT devices and ML-based decision-making into legacy irrigation systems
•	Economic and practical considerations of transitioning from traditional to automated irrigation management
6.3. Integration with Other Precision Agriculture Technologies
•	Synergies between automated irrigation and technologies such as remote sensing, variable rate application, and yield mapping, focusing on how they contribute to real-time, automated irrigation management
•	Benefits and challenges of integrating these technologies to create a holistic precision agriculture ecosystem

7. MONITORING AND ENSURING SYSTEM RELIABILITY
7.1. Resilience and Fault Tolerance
•	Strategies for ensuring the robustness and reliability of the system in the face of failures, disruptions, or unexpected events
•	The role of redundancy, failover mechanisms, and self-healing capabilities in maintaining system stability and minimizing downtime
•	The potential of using AI techniques for anomaly detection, fault diagnosis, and predictive maintenance in real-time irrigation systems
7.2. Importance of Monitoring in Automated Irrigation Systems
•	Ensuring system stability, detecting anomalies, and preventing errors from propagating
•	Consequences of system failures and the need for robust monitoring
7.3. Advanced Monitoring Techniques
•	Remote monitoring using cameras and sensors integrated with the cloud
•	Innovative approaches for real-time system health assessment
7.4. Closed-Loop Control and System Security
•	Exploring the concept of closed-loop control in autonomous irrigation systems
•	Addressing security concerns and potential risks of fully automated systems
•	Strategies for managing and mitigating risks in large-scale deployments
CASE STUDIES AND REAL-WORLD IMPLEMENTATIONS
•	Detailed case studies showcasing the successful deployment of end-to-end automated irrigation systems in various agricultural settings
•	Lessons learned, challenges encountered, and best practices derived from real-world implementations
•	Emphasis on how each case study demonstrates the effectiveness and efficiency of integrated, real-time automated irrigation management
CONCLUSION/FUTURE DIRECTIONS AND UNANSWERED QUESTIONS
•	Summarize the key insights gained from the question-driven review, emphasizing how each section contributes to the overarching goal of achieving real-time, end-to-end automation in irrigation management
•	Based on the questions addressed, propose new research directions and unanswered questions
•	Identify key research gaps and propose concrete research questions and hypotheses for advancing the field of real-time, automated irrigation management
•	Highlight the need for collaborative research efforts across disciplines, such as computer science, agricultural engineering, and environmental science, to address the complex challenges of automated irrigation systems
•	Emphasize the need for further innovation and exploration in real-time, automated irrigation systems


"""

review_intention = """  
the purpose and intention of this systematic review on automated systems for real-time irrigation management can be interpreted as follows:
Addressing the global food challenge: The review aims to explore how automated, real-time irrigation management systems can contribute to the efficient use of water resources and enhance agricultural productivity to meet the growing demand for food.
Evaluating the current state and future potential: The primary objective is to critically assess the current state of end-to-end automated irrigation management systems that integrate IoT and machine learning technologies. The review also seeks to identify gaps and propose solutions for seamless integration across the automated irrigation management system to achieve fully autonomous, scalable irrigation management.
Examining automation across the entire pipeline: The review intends to systematically analyze the automation of each component of the irrigation management pipeline, from data collection and transmission to processing, analysis, decision-making, and automated action. It aims to investigate the effectiveness and efficiency of integrated end-to-end automated irrigation systems.
Highlighting the role of interoperability and standardization: The review seeks to emphasize the importance of interoperability and standardization in enabling the integration of components within the automated irrigation management pipeline. It aims to identify existing and emerging standards and their applicability to real-time irrigation management systems.
Identifying challenges and proposing solutions: The review intends to uncover the challenges associated with implementing real-time, automated irrigation systems, such as data quality, scalability, reliability, and security. It aims to propose solutions and best practices based on the analysis of case studies and real-world implementations.
Guiding future research and innovation: By identifying research gaps and proposing new research questions and hypotheses, the review aims to provide a roadmap for advancing the field of real-time, automated irrigation management. It seeks to encourage collaborative research efforts across disciplines to address the complex challenges of automated irrigation systems.
In summary, this systematic review aims to provide a comprehensive and critical evaluation of the current state and future potential of real-time, end-to-end automated irrigation management systems. Its intention is to guide future research, innovation, and implementation efforts to achieve fully autonomous, scalable irrigation management that can contribute to addressing the global food challenge."""

section_intentions = {
    "1": "INTRODUCTION: Sets the context for the systematic review by highlighting the global food challenge, the critical role of irrigation, and the potential for automation and integration across the irrigation management pipeline.",
    "2": "REVIEW METHODOLOGY: Outlines the question-driven framework used to guide the literature review, presenting key research questions, motivations, and hypotheses for a structured approach to assessing real-time, autonomous irrigation management systems.",
    "3": "DATA COLLECTION TO CLOUD: AUTOMATION AND REAL-TIME PROCESSING: Focuses on the initial stages of the automated irrigation management pipeline, covering data collection, edge and fog computing, real-time data transmission protocols and technologies, and the challenges and solutions associated with real-time data transmission.",
    "4": "AUTOMATED DATA PROCESSING IN THE CLOUD: Examines the importance of data quality and preprocessing in the cloud, containerization strategies for scalable and autonomous deployment, and the deployment of machine learning (ML) models for real-time data processing and inference.",
    "5": "GENERATING AND APPLYING IRRIGATION INSIGHTS: Focuses on the application of ML-generated insights to control irrigation systems without manual intervention, investigating the real-time generation and automated application of actionable irrigation insights, and the importance of interpretability and explainability in ML models.",
    "6": "INTEGRATION, INTEROPERABILITY, AND STANDARDIZATION: Explores the challenges and strategies for integrating automated systems with existing irrigation infrastructure and other precision agriculture technologies, highlighting the importance of interoperability and standardization in enabling seamless communication and compatibility.",
    "7": "MONITORING AND ENSURING SYSTEM RELIABILITY: Focuses on strategies for ensuring the robustness and reliability of the automated irrigation system, including resilience and fault tolerance, advanced monitoring techniques, closed-loop control, and addressing security concerns and risks in large-scale deployments.",
    "8": "CASE STUDIES AND REAL-WORLD IMPLEMENTATIONS: Presents detailed examples of successful deployments of end-to-end automated irrigation systems in various agricultural settings, highlighting lessons learned, challenges encountered, and best practices derived from real-world implementations.",
    "9": "CONCLUSION/FUTURE DIRECTIONS AND UNANSWERED QUESTIONS: Summarizes key insights gained from the question-driven review, identifies research gaps, proposes new research directions and unanswered questions for advancing the field, and emphasizes the need for collaborative research efforts and further innovation in real-time, automated irrigation management.",
}

scopus_search_guide = """
Syntax and Operators

Valid syntax for advanced search queries includes:

*   Field codes (e.g. TITLE, ABS, KEY, AUTH, AFFIL) to restrict searches to specific parts of documents
*   Boolean operators (AND, OR, AND NOT) to combine search terms
*   Proximity operators (W/n, PRE/n) to find words within a specified distance
*   Quotation marks for loose/approximate phrase searches
*   Braces {} for exact phrase searches
*   Wildcards (* and ?) for partial word matches

Invalid syntax includes:

*   Mixing different proximity operators (e.g. W/n and PRE/n) in the same expression
*   Using wildcards or proximity operators with exact phrase searches
*   Placing AND NOT before other Boolean operators
*   Using wildcards on their own without any search terms

Ideal Search Structure

An ideal advanced search query should:

*   Use field codes to focus the search on the most relevant parts of documents
*   Combine related concepts using AND and OR
*   Exclude irrelevant terms with AND NOT at the end
*   Use proximity operators to find phrases and related words near each other
*   Employ quotation marks and braces appropriately for phrase searching
*   Include wildcards to capture variations of key terms
*   Follow the proper order of precedence for operators

Complex searches should be built up systematically, with parentheses to group related expressions as needed. The information from the provided documents on syntax rules and operators should be applied rigorously.

Example Advanced Searches

scopus_queries:
  - TITLE-ABS-KEY("precision agriculture" AND ("machine learning" OR "artificial intelligence") AND water W/10 management)
  - TITLE(({internet of things} OR iot) W/15 (irrigation OR watering) AND sensor?)
  - TITLE-ABS(("precision farming" OR "precision agriculture") AND ("deep learning" OR "neural network?") AND water conservation)
  - TITLE-ABS-KEY((crop? PRE/5 monitor?) AND "remote sensing" AND (irrigation OR water?))
  - AFFIL("agricultural engineering") AND TITLE-ABS(("precision agriculture" OR "smart farming") AND soil W/10 moist?)
  - TITLE(("precision irrigation" OR "variable rate irrigation") AND "machine learning")
  - TITLE-ABS-KEY(("precision agriculture" OR "precision farming") AND (autonom? W/5 robot?) AND (irrigat? OR water?))
  - ALL(("internet of things" OR iot) AND (soil W/10 (monitor? OR sens?)) AND ("crop yield" OR productivity))
  - TITLE-ABS(("digital agriculture" OR "smart agriculture") AND "big data" AND irrigation W/10 schedul?)
  - AFFIL("precision agriculture") AND TITLE-ABS-KEY(("machine learning" OR "artificial intelligence") AND water W/15 (productivity OR efficiency OR sav?))



These example searches demonstrate different ways to effectively combine key concepts related to precision agriculture, irrigation, real-time monitoring, IoT, machine learning and related topics using advanced search operators. They make use of field codes, Boolean and proximity operators, phrase searching, and wildcards to construct targeted, comprehensive searches to surface the most relevant research. The topic focus is achieved through carefully chosen search terms covering the desired themes.
"""

google_search_guide = """
          Syntax and Operators
Valid syntax for advanced Google search queries includes:

Using quotation marks " " for exact phrase matches
Adding a minus sign - before terms to exclude them
Employing the OR operator in all caps to find pages containing either term
Using the site: operator to limit results to a specific website
Applying the filetype: operator to find specific file formats like PDF, DOC, etc.
Adding the * wildcard as a placeholder for unknown words
Invalid syntax includes:

Putting a plus sign + before words (Google stopped supporting this)
Using other special characters like ?, $, &, #, etc. within search terms
Explicitly using the AND operator (Google's default behavior makes it redundant)
Ideal Search Structure
An effective Google search query should:

Start with the most important search terms
Use specific, descriptive keywords related to irrigation scheduling, management, and precision irrigation
Utilize exact phrases in quotes for specific word combinations
Exclude irrelevant terms using the minus sign
Connect related terms or synonyms with OR
Apply the * wildcard strategically for flexibility
Limit to particular sites or domains for focused searches, if needed
Specify desired file types if only certain document formats are wanted
Searches should be concise yet precise, following the syntax rules carefully. If a topic is complex, consider performing multiple related searches instead of an overly complicated single query.

Example Searches
google_queries:
- '"precision irrigation" ("soil moisture sensors" OR "evapotranspiration") "irrigation scheduling"'
- '"machine learning" "irrigation management" -"deep learning"'
- '"IoT sensors" "real-time" ("soil moisture monitoring" OR "crop water stress") "precision irrigation"'
- '"remote sensing" "vegetation indices" "irrigation scheduling" -"satellite imagery"'
- '"wireless sensor networks" "variable rate irrigation" "precision agriculture"'
- '"MQTT protocol" "real-time" "smart irrigation system"'
- '"machine learning" "crop water demand prediction" "precision irrigation"'
- '"decision support system" ("irrigation scheduling" OR "irrigation management") -"web-based"'
- '"sensor data fusion" "irrigation optimization" "machine learning"'
- '"IoT platform" "irrigation automation" "precision agriculture" -"smart home"'

** Note that we need to enclose each search query within single quotes to treat them as single strings in YAML, otherwise the quotes within the queries would cause parsing errors if not properly escaped. **


These example searches demonstrate how to create targeted, effective Google searches related to irrigation scheduling, management, and precision irrigation. They focus on specific topics, exclude irrelevant results, allow synonym flexibility, and limit to relevant domains when needed.

The search terms are carefully selected to balance relevance and specificity while avoiding being overly restrictive. By combining relevant keywords, exact phrases, and operators, these searches help generate high-quality results for the given topics.
"""


def remove_illegal_characters(text):
    if text is None:
        return ""
    illegal_chars = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")
    return illegal_chars.sub("", str(text))


def get_prompt(template_name, **kwargs):
    prompts = {
        "paper_analysis": """<instructions>
First, carefully read through the full text of the paper provided under <full_text>. Then, analyze the paper's relevance to the specific point mentioned in <point_content> within the context of the overall literature review outline and intention provided.

Your analysis should include:

A concise summary (3-5 sentences) of the key points of the paper as they relate to the outline point.
A detailed explanation of how the specifics of the paper contribute to addressing the point within the larger context and intent of the literature review. Consider the following factors based on the paper type:
Relevance: How directly does the paper address the key issues pertaining to the outline point?
Insight: To what extent does the paper provide novel, meaningful, or valuable information for the point?
Credibility: How reliable, valid, and trustworthy are the paper's findings, methods, or arguments?
Scope: How comprehensive is the paper's coverage of topics relevant to the outline point?
Recency: How up-to-date is the information in the context of the current state of knowledge on the topic?
The two most relevant verbatim quotes from the paper, each no more than 3 sentences, demonstrating its pertinence to the outline point and review. Include the most important quote under "extract_1" and the second most important under "extract_2". If no quotes are directly relevant, leave these blank.
A relevance score between 0 and 1 representing the overall fit of the paper to the outline point and review. Use the following rubric:
0.9-1.0: Exceptionally relevant - Comprehensively addresses all key aspects of the point with highly insightful, reliable, and up-to-date information. A must-include for the review.
0.8-0.89: Highly relevant - Addresses key issues of the point with novel, credible, and meaningful information. Adds substantial value to the review.
0.7-0.79: Very relevant - Directly informs the point with reliable and valuable information, but may have minor limitations in scope, depth, or recency.
0.6-0.69: Moderately relevant - Provides useful information for the point, but has some notable gaps in addressing key issues or limitations in insight, credibility, or timeliness.
0.5-0.59: Somewhat relevant - Addresses aspects of the point, but has significant limitations in scope, depth, reliability, or value of information. May still be worth including.
0.4-0.49: Marginally relevant - Mostly tangential to the main issues of the point, with information of limited insight, credibility, or meaningfulness. Likely not essential.
0.2-0.39: Minimally relevant - Only briefly touches on the point with information that is of questionable value, reliability, or timeliness. Not recommended for inclusion.
0.0-0.19: Not relevant - Fails to address the point or provide any useful information. Should be excluded from the review.

Be uncompromising in assigning the most appropriate score based on a holistic assessment of the paper's merits and limitations.

If the paper is highly relevant (0.8+) to a different outline section, indicate the most applicable subsection under "alternate_section" in the format "1.2". If no other section applies, leave this blank.
List any important limitations of the paper for fully addressing the point and outline, such as limited scope, methodological issues, dated information, or tangential focus. If there are no major limitations, leave this blank.
Provide your analysis in the following JSON format:

<response_format>
{{
"explanation": "",
"extract_1": "",
"extract_2": "",
"relevance_score": 0.0,
"Alternate_section": "",
"limitations": "",
"inline_citation": "",
"apa_citation": ""
}}
</response_format>

Also include a suggested in-line citation for the paper under "inline_citation" in the format (Author, Year), and a full APA style reference under "apa_citation".
Leave any fields blank if not applicable.
</instructions>

<documents> <full_text> {full_text} </full_text> <context> <outline> {outline} </outline>
<review_intention>
{review_intention}
</review_intention>

<point_content>
{point_content}
</point_content>

<subsection_title>

{section_title}
</subsection_title>

<section_title>
{document_title}

</section_title>
</context>
</documents>
""",
        "generate_queries": """
      <documents>

  <document index="1">

  <source>search_query_prompt.txt</source>

  <document_content>

  <instructions>

  Carefully review the provided context, including the overall review intention under <review_intention>, the purpose of the current section within that context explained in <section_intention>, and the specific point that needs to be addressed by the literature search, given in <point_content>.

  Your task is to generate a set of 10 highly optimized search queries that would surface the most relevant, insightful, and comprehensive set of research articles to shed light on various aspects of the particular point <point_content> which is under subsection <subsection_title>, while keeping the queries tightly focused around the intentions of the <section_title> and <review_intention>.

  The queries should:

  - Be thoughtfully crafted to return results that directly address the key issues and nuances of the <point_content>

  - Demonstrate creativity and variety in their formulation to capture different dimensions of the topic

  - Use precise terminology and logical operators to maintain a high signal-to-noise ratio in the results

  - Cover a broad range of potential subtopics, perspectives, and article types related to the <point_content>

  - Align closely with the stated goals of the <section_title> and <review_intention> to maximize relevance

  - Adhere strictly and diligently to any specific guidance or requirements provided in <search_guidance>. This is critical!

  Provide your response strictly in the following XML format:
  <(search)_queries>
  <query>query_1</query>
  <query>query_2</query>
  <query>query_3</query>
  <query>query_4</query>
  <query>query_5</query>
  <query>query_6</query>
  <query>query_7</query>
  <query>query_8</query>
  <query>query_9</query>
  <query>query_10</query>
  </(search)_queries>

  The (search) platform will be specified in the search guidance. Replace (search) with the platform name (e.g., scopus_queries, google_queries).

  Each query_n should be replaced with a unique, well-formulated search entry according to the instructions in <search_guidance>. No other text should be included. Any extraneous text or deviation from this exact format will result in an unusable output.
  </instructions>

  <resources>

  <review_intention>

  {review_intention}

  </review_intention>

  <section_intention>

  {section_intention}

  </section_intention>

  <point_content>

  {point_content}

  </point_content>

  <section_title>

  {section_title}

  </section_title>

  <subsection_title>

  {subsection_title}

  </subsection_title>

  <search_guidance>

  {search_guidance}

  </search_guidance>

  </resources>

  </document_content>

  </document>

  </documents>
""",
    }
    return prompts[template_name].format(**kwargs)
