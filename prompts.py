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

review_intention = """  the purpose and intention of this systematic review on automated systems for real-time irrigation management can be interpreted as follows:
Addressing the global food challenge: The review aims to explore how automated, real-time irrigation management systems can contribute to the efficient use of water resources and enhance agricultural productivity to meet the growing demand for food.
Evaluating the current state and future potential: The primary objective is to critically assess the current state of end-to-end automated irrigation management systems that integrate IoT and machine learning technologies. The review also seeks to identify gaps and propose solutions for seamless integration across the automated irrigation management system to achieve fully autonomous, scalable irrigation management.
Examining automation across the entire pipeline: The review intends to systematically analyze the automation of each component of the irrigation management pipeline, from data collection and transmission to processing, analysis, decision-making, and automated action. It aims to investigate the effectiveness and efficiency of integrated end-to-end automated irrigation systems.
Highlighting the role of interoperability and standardization: The review seeks to emphasize the importance of interoperability and standardization in enabling the integration of components within the automated irrigation management pipeline. It aims to identify existing and emerging standards and their applicability to real-time irrigation management systems.
Identifying challenges and proposing solutions: The review intends to uncover the challenges associated with implementing real-time, automated irrigation systems, such as data quality, scalability, reliability, and security. It aims to propose solutions and best practices based on the analysis of case studies and real-world implementations.
Guiding future research and innovation: By identifying research gaps and proposing new research questions and hypotheses, the review aims to provide a roadmap for advancing the field of real-time, automated irrigation management. It seeks to encourage collaborative research efforts across disciplines to address the complex challenges of automated irrigation systems.
In summary, this systematic review aims to provide a comprehensive and critical evaluation of the current state and future potential of real-time, end-to-end automated irrigation management systems. Its intention is to guide future research, innovation, and implementation efforts to achieve fully autonomous, scalable irrigation management that can contribute to addressing the global food challenge."""


def remove_illegal_characters(text):
    if text is None:
        return ""
    illegal_chars = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")
    return illegal_chars.sub("", str(text))


def get_prompt(template_name, **kwargs):
    prompts = {
        "paper_analysis": """<instructions>
First, carefully read through the full text of the research paper provided under <full_text>. Then, analyze the paper's relevance to the specific point mentioned in <point_text> within the context of the overall literature review outline and intention provided.

Your analysis should include:

A concise summary (3-5 sentences) of the key points of the paper as they relate to the outline point. Then explain in detail how the specifics of the paper contribute to addressing the point within the larger context and intent of the literature review. Consider the directness, detail, recency and methodological soundness of the paper's findings for the topic.
The two most relevant verbatim quotes from the paper, each no more than 3 sentences, that demonstrate its pertinence to the outline point and review. Include the most important quote under "extract_1" and the second most important under "extract_2". If no quotes are directly relevant, leave these blank.
A relevance score between 0 and 1 representing the overall fit of the paper to the outline point and review. Use the following rubric:
0.9-1.0: Directly addresses point with highly relevant, recent, rigorous findings
0.7-0.8: Substantially informs point with relevant, sound findings
0.4-0.6: Somewhat relevant to point but limited in scope, detail or rigor
0.1-0.3: Minimally relevant with only tangential or methodologically weak findings
0.0: Not at all relevant to outline point or review Be uncompromising in assigning the most appropriate score.
If the paper is highly relevant (0.8+) to a different section of the outline than the one specified, indicate the most applicable subsection under "Alternate_section" in the format "1.2". If no other section applies, leave this blank.
List any important limitations of the paper for fully addressing the point and outline. This could include:
Narrow scope that misses key issues
Methodological weaknesses that limit reliability
Dated findings that may not reflect current understanding
Insufficient depth or detail on relevant topics
Tangential focus on less pertinent aspects If there are no major limitations, leave this blank.
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

<point_text>
{point_text}
</point_text>

<subsection_title>

{section_title}
</subsection_title>

<section_title>
{document_title}

</section_title>
</context>
</documents>
""",
        # Older version of the prompt
        "process_scopus_results": """

   <instructions>

   Based on the provided outline, the intention of the review, and the specific point mentioned, read through the given research papers (including titles, abstracts, DOIs, journal information, and citation counts). The goal is to identify the paper whose abstract most strongly relates to or supports the given point in the context of the review outline.

   The selection criteria, in order of importance, are:

   1. Relatedness of the abstract to the given point and review outline

   2. Reputability or prestige of the journal in which the paper is published

   3. Number of citations the paper has received

   After considering these criteria, return your response as a valid JSON array, where each element is an object with five key-value pairs: "doi" for the DOI of the related paper, "title" for the title of the related paper, "citation_count" for the number of citations the paper has received, "relevance_score" for a score between 0 and 1 representing the overall fit and relevance of the paper to the point in particular and the paper in general, and "journal" for the name of the journal in which the paper is published. Be parsimonious yet fair in assigning the relevance scores. Do not include any additional text or deviation from the specified JSON format.
   
   Critical: You much return a maximum of the top three most relevant papers based on the given point and the review intention. If there are fewer than three papers, return the available papers. If there are no papers, return an empty array.

   </instructions>

   <prompt>

   <context>

   <outline>

   <!-- Outline content provided here -->

   {outline}

   </outline>

   <review_intention>

   <!-- Review intention provided here -->

   {review_intention}

   </review_intention>

   <point>

   <!-- Specific point provided here -->

   {point}

   </point>

   <research_papers>

   <!-- List of research papers with titles, abstracts, DOIs, journal information, and citation counts provided here -->

   {research_papers}

   </research_papers>

   </context>

   <response_format>

    [
    {
      "doi": "", /* Obtain the exact doi from the provided <research_papers> </research_papers>. Leave blank if none. */
      "title": "", /* Obtain the exact paper title from the provided <research_papers> </research_papers>. */
      "citation_count": "", /* Obtain the exact citation count from the provided <research_papers> </research_papers>. Leave blank if none. */
      "relevance_score": 0.0, /* Insert a parsimonious relevance score based on the given point, the paper's abstract and the review intention */
      "journal": "" /* Obtain the exact journal name from the provided <research_papers> </research_papers>. Leave blank if none. */
    },
    {
      "doi": "",
      "title": "",
      "citation_count": "",
      "relevance_score": 0.0,
      "journal": ""
    },
    {
      "doi": "",
      "title": "",
      "citation_count": "",
      "relevance_score": 0.0,
      "journal": ""
    }
  ]

   </response_format>

   </prompt>

   """,
    }
    return prompts[template_name].format(**kwargs)
