import re

previous_sections = """
A systematic review of automated systems for real-time irrigation management

1. INTRODUCTION
The challenge of feeding a growing population with finite resources is becoming increasingly pressing. By 2050, the world population is expected to reach 9.7 billion, necessitating a 70% increase in food production (Falkenmark and Rockstrom, 2009). Irrigation plays a crucial role in enhancing crop yields and agricultural productivity to meet this growing demand. Studies have shown that irrigation can significantly increase crop water productivity, contributing to increased food production (Ali and Talukder, 2008; Playan and Mateos, 2005). However, water scarcity poses a significant challenge, with many regions facing water deficits and the need for improved water management practices (Falkenmark and Rockstrom, 2009). Optimizing irrigation schedules and doses based on crop requirements and environmental conditions is essential for maximizing yield and quality while minimizing water use (Zhang et al., 2024). The necessity of scalable water-efficient practices for increasing food demand cannot be overstated. Techniques such as regulated deficit irrigation, magnetically treated water, and the use of drought-tolerant crops like sorghum have shown promise in improving water productivity and ensuring food security (Mehmood et al., 2023; Putti et al., 2023; Hadebe et al., 2016). As the global food challenge intensifies, it is imperative to critically evaluate the current state and future potential of irrigation management systems to guide research, innovation, and implementation efforts towards fully autonomous, scalable solutions.

Despite the importance of irrigation in addressing the global food challenge, traditional irrigation management techniques, such as manual scheduling and timer-based systems, have significant limitations. These methods are often labor-intensive, inefficient, and less adaptable to changing conditions (Savin et al., 2023). Manual and timer-based scheduling can lead to high operational costs and inefficient water use (Raghavendra, Han, and Shin, 2023). The reliance on manual intervention and predetermined schedules limits their adaptability to changing environmental conditions, crop water requirements, and soil moisture levels (Kaptein et al., 2019). Sensor-based irrigation systems offer an alternative, enabling real-time adjustments based on soil water status measurements (Kaptein et al., 2019). However, the adoption of these systems in commercial settings has been limited, often requiring extensive input from researchers (Kim et al., 2014; Lea-Cox et al., 2018; Ristvey et al., 2018). The limitations of traditional irrigation management techniques highlight the need for scalable, automated solutions for greater efficiency in irrigation management. Automated systems that collect real-time data, analyze it, and make autonomous irrigation decisions can lead to improved water use efficiency and increased crop productivity (Champness et al., 2023; Wu et al., 2022). To fully understand the potential of automated systems, it is necessary to examine the automation of each part of the irrigation management pipeline and analyze the effectiveness and efficiency of integrated end-to-end solutions.

The emergence of smart irrigation management and IoT marks a significant shift from historical irrigation practices. Modern approaches rely on vast data and analysis algorithms, leveraging technologies such as remote sensing, sensor networks, weather data, and computational algorithms (Atanasov, 2023; Bellvert et al., 2023; Kumar et al., 2023). IoT plays a vital role in collecting vast amounts of data through sensors, data transmission, and tailored networks, enabling real-time monitoring and control of irrigation systems (Liakos, 2023; Zuckerman et al., 2024). These advancements in data collection and analysis have the potential to revolutionize irrigation management, allowing for more precise and efficient water use. However, challenges such as processing diverse data sources, data integration, and lack of integrated data analysis hamper the full benefit of IoT in irrigation management (Dave et al., 2023). The current fragmented approach in smart irrigation, focusing on individual components rather than the entire system, limits the potential for fully autonomous, real-time end-to-end irrigation management (Togneri et al., 2021). To address these challenges and fully realize the potential of smart irrigation management, there is a need for automating and integrating each section of the irrigation management pipeline, from sensor/weather data collection and transmission to processing, analysis, decision-making, and automated action (McKinion and Lemmon, 1985). This integration requires a thorough investigation of the role of interoperability and standardization in enabling seamless communication and compatibility between components within the automated irrigation management pipeline.

Machine learning (ML) plays a significant role in processing vast data, predicting plant stress, modeling climate effects, and optimizing irrigation in smart irrigation management systems. ML algorithms can analyze data collected from sensors and weather stations to determine optimal irrigation schedules (Vianny et al., 2022). However, the potential of ML is often constrained by manual steps, such as data interpretation, decision-making on irrigation timing and volume, and system adjustments. Automating ML integration to allow direct action from insights to irrigation execution, removing bottlenecks and achieving real-time adaptability, is crucial for fully autonomous irrigation management (Barzallo-Bertot et al., 2022). By integrating ML into automated systems, the irrigation management pipeline can become more seamless and efficient, enabling real-time decision-making and action based on data-driven insights. To achieve this level of automation and integration, it is essential to identify gaps and propose solutions for seamless integration across the automated irrigation management system, aiming to achieve fully autonomous, scalable irrigation management.

To achieve seamless integration across the automated irrigation management system, interoperability and standardization are critical. Interoperability allows different system components, such as sensors, actuators, and software, to communicate and exchange data effectively, while standardization ensures that data is represented in a consistent format (Santos et al., 2020). Standardized protocols and data formats are essential for achieving seamless integration and ensuring compatibility between components in real-time irrigation management systems (Robles et al., 2022; Hatzivasilis et al., 2018). Existing and emerging standards, such as OGC SensorThings API and ISO 11783, have applicability to real-time irrigation management systems (Hazra et al., 2021). However, challenges such as data quality, scalability, reliability, and security need to be addressed to fully realize the potential of interoperability and standardization in automated irrigation management systems (Hazra et al., 2021). Addressing these challenges is crucial for enabling the seamless integration of components within the automated irrigation management pipeline, which is essential for achieving fully autonomous, scalable irrigation management. A comprehensive evaluation of the role of interoperability and standardization in enabling the integration of components within the automated irrigation management pipeline is necessary to guide future research and implementation efforts.
The primary objective of this systematic review is to critically evaluate the current state and future potential of real-time, end-to-end automated irrigation management systems that integrate IoT and machine learning technologies for enhancing agricultural water use efficiency and crop productivity.
Specific objectives include:
•	Examining the automation of each part of the irrigation management pipeline and the seamless integration of each section in the context of irrigation scheduling and management.
•	Analyzing the effectiveness and efficiency of integrated end-to-end automated irrigation systems.
•	Investigating the role of interoperability and standardization in enabling the integration of components within the automated irrigation management pipeline.
•	Identifying gaps and proposing solutions for seamless integration across the automated irrigation management system, aiming to achieve fully autonomous, scalable irrigation management.
By addressing these objectives, this systematic review aims to provide a comprehensive and critical evaluation of the current state and future potential of real-time, end-to-end automated irrigation management systems. Its intention is to guide future research, innovation, and implementation efforts to achieve fully autonomous, scalable irrigation management that can contribute to addressing the global food challenge.

2. REVIEW METHODOLOGY
•	Question-driven framework to guide the literature review of real-time, autonomous irrigation management systems
•	Key research questions posed, each with the motivation behind investigating them and a starting hypothesis to evaluate against the examined literature
•	Table presenting the major objectives, specific objectives, questions, motivations, and hypotheses
3. DATA COLLECTION TO CLOUD: AUTOMATION AND REAL-TIME PROCESSING
3.1. Irrigation management data
The success of automated irrigation management systems relies heavily on the collection, transmission, and analysis of various types of data. The most applicable data types for irrigation management include soil moisture, canopy temperature, weather data, and plant physiological parameters (Farooq et al., 2019; Li et al., 2019; Olivier et al., 2021; Evett et al., 2020). These data are typically collected from a range of sources, including in-field sensors, remote sensing platforms, weather stations, and manual measurements (Li et al., 2019; Karimi et al., 2018).
Soil moisture data is arguably the most critical type of data for irrigation management, as it directly reflects the water available to plants and can be used to determine the optimal timing and amount of irrigation (Olivier et al., 2021; Intrigliolo & Castel, 2006). Soil moisture sensors, such as tensiometers, capacitance probes, and time-domain reflectometry (TDR) sensors, can provide real-time measurements of soil water content at various depths (Farooq et al., 2019). These sensors can be deployed in a network configuration to capture spatial variability in soil moisture across a field (Karimi et al., 2018).
Canopy temperature data is another valuable type of data for irrigation management, as it can be used to assess plant water stress and adjust irrigation accordingly (Evett et al., 2020). Infrared thermometers and thermal cameras can be used to measure canopy temperature, which is influenced by factors such as air temperature, humidity, wind speed, and plant water status (Li et al., 2019). When plants experience water stress, they tend to close their stomata to reduce water loss, leading to an increase in canopy temperature (Evett et al., 2020). By monitoring canopy temperature and comparing it to reference values, automated irrigation systems can detect plant water stress and trigger irrigation events to maintain optimal plant health and productivity (Li et al., 2019).
Weather data, including temperature, humidity, precipitation, wind speed, and solar radiation, are essential for predicting crop water requirements and scheduling irrigation events (Akilan & Baalamurugan, 2024). Weather stations equipped with various sensors can provide real-time measurements of these parameters, which can be used as inputs for crop water requirement models, such as the FAO-56 Penman-Monteith equation (Li et al., 2019). These models estimate crop evapotranspiration (ET) based on weather data and crop-specific coefficients, allowing for the calculation of irrigation requirements (Intrigliolo & Castel, 2006). By integrating weather data into automated irrigation systems, irrigation schedules can be dynamically adjusted based on changing environmental conditions, ensuring that crops receive the optimal amount of water at the right time (Akilan & Baalamurugan, 2024).
When collecting and utilizing these data types, several considerations must be taken into account, including the volume, frequency, format, and source of the data (Farooq et al., 2019). The volume of data generated by automated irrigation systems can be substantial, especially when high-resolution sensors are deployed at a large scale (Bastidas Pacheco et al., 2022). This necessitates the use of efficient data storage, processing, and transmission technologies to handle the data load (Farooq et al., 2019). The frequency of data collection is another important consideration, as it directly impacts the temporal resolution of the data and the ability to detect rapid changes in plant water status or environmental conditions (Bastidas Pacheco et al., 2022). Bastidas Pacheco et al. (2022) demonstrated that collecting full pulse resolution data from water meters provides more accurate estimates of event occurrence, timing, and features compared to aggregated temporal resolutions, highlighting the importance of selecting appropriate data collection frequencies to ensure the quality and usefulness of the data for irrigation management.
The format of the data is also crucial, as it determines the compatibility and interoperability of the data with various analysis tools and platforms (Farooq et al., 2019). Standardized data formats, such as JSON, XML, or CSV, can facilitate data exchange and integration between different components of the automated irrigation system (Zhang et al., 2023). The source of the data is another important consideration, as it can impact the reliability, accuracy, and spatial coverage of the data (Farooq et al., 2019). For example, in-field sensors provide highly localized measurements, while remote sensing platforms, such as satellites or drones, can provide data at larger spatial scales (Li et al., 2019). By combining data from multiple sources, automated irrigation systems can achieve a more comprehensive understanding of crop water requirements and optimize irrigation management accordingly (Farooq et al., 2019).
Data quality, accuracy, and reliability are paramount in irrigation management, as they directly impact the effectiveness of decision-making processes and the efficiency of water use (Gupta et al., 2020). Inaccurate or unreliable data can lead to suboptimal irrigation decisions, resulting in crop stress, yield losses, or wasted water resources (Ramli & Jabbar, 2022). Gupta et al. (2020) emphasized the critical importance of data security and privacy in smart farming systems, as the leakage of sensitive agricultural data can cause severe economic losses to farmers and compromise the integrity of the automated irrigation system. The authors also highlighted the need for robust authentication and secure communication protocols to prevent unauthorized access to smart farming systems and protect data in transit (Gupta et al., 2020).
Ramli and Jabbar (2022) addressed the challenges associated with implementing real-time, automated irrigation systems, including data quality, scalability, reliability, and security. They proposed solutions and best practices based on the analysis of case studies and real-world implementations, such as the use of redundant sensors, data validation techniques, and secure communication protocols (Ramli & Jabbar, 2022). The authors also emphasized the importance of regular maintenance and calibration of sensors to ensure the accuracy and reliability of the collected data (Ramli & Jabbar, 2022).
Researchers have investigated the use of data compression, aggregation, and filtering techniques to reduce bandwidth requirements and improve transmission efficiency in automated irrigation systems (Karim et al., 2023; Rady et al., 2020; Cui, 2023). Karim et al. (2023) explored the effectiveness of various data compression techniques, such as lossless and lossy compression algorithms, in reducing the size of data packets transmitted over wireless networks. The authors found that lossless compression techniques, such as Huffman coding and Lempel-Ziv-Welch (LZW), can significantly reduce data size without compromising data quality, while lossy compression techniques, such as JPEG and MP3, can further reduce data size by introducing acceptable levels of distortion (Karim et al., 2023).
Rady et al. (2020) developed a novel data compression algorithm specifically designed for irrigation data, which achieved significant compression ratios without compromising data quality. The authors demonstrated that their algorithm could reduce the amount of data transmitted over wireless networks, thereby improving the efficiency of the irrigation system and reducing costs (Rady et al., 2020). Cui (2023) investigated the use of data aggregation and filtering techniques to reduce the number of transmissions and save bandwidth in automated irrigation systems. The author proposed a data aggregation scheme that combines multiple sensor readings into a single value, such as the average soil moisture over a specified time interval, to reduce the frequency of data transmissions (Cui, 2023). Additionally, the author explored the use of data filtering techniques, such as Kalman filters and particle filters, to remove noise and outliers from sensor data, improving the accuracy and reliability of the transmitted information (Cui, 2023).
Data standardization and harmonization are crucial for facilitating seamless integration and interoperability between the various components of automated irrigation management systems (Zhang et al., 2023; Ermoliev et al., 2022). Zhang et al. (2023) developed a novel cyberinformatics technology called iCrop, which enables the in-season monitoring of crop-specific land cover across the contiguous United States. The authors highlighted the importance of data standardization and harmonization in the context of iCrop, as it allows for the efficient distribution of crop-specific land cover information based on the findable, accessible, interoperable, and reusable (FAIR) data principle (Zhang et al., 2023). By adopting standardized data formats and protocols, such as the Open Geospatial Consortium (OGC) standards, iCrop enables the seamless integration of various data sources and facilitates the interoperability of the system with other agricultural decision support tools (Zhang et al., 2023).
Ermoliev et al. (2022) proposed a linkage methodology for linking distributed sectoral/regional optimization models in a situation where private information is not available or cannot be shared by modeling teams. The authors emphasized the need for data standardization to enable decentralized cross-sectoral coordination and analysis, as it allows for the consistent representation and exchange of data between different models and stakeholders (Ermoliev et al., 2022). By adopting standardized data formats and interfaces, the proposed linkage methodology can facilitate the integration of various optimization models and support the development of comprehensive decision support systems for sustainable resource management (Ermoliev et al., 2022).
Metadata plays a vital role in providing context and enabling better data interpretation and decision-making in automated irrigation management systems (Jahanddideh-Tehrani et al., 2021). Metadata refers to the additional information that describes the characteristics, quality, and context of the primary data, such as the sensor type, calibration parameters, measurement units, and timestamp (Jahanddideh-Tehrani et al., 2021). Jahanddideh-Tehrani et al. (2021) highlighted the importance of metadata in water resources management, as it enables decision-makers to use the data to the best of its capabilities by understanding factors such as when water data was collected and what factors might have contributed to the measurements. The authors emphasized the need for standardized metadata formats and guidelines, such as the Dublin Core Metadata Initiative (DCMI) and the ISO 19115 standard, to ensure the consistency and interoperability of metadata across different water information systems (Jahanddideh-Tehrani et al., 2021).
In the context of automated irrigation management systems, metadata can provide valuable information about the data collection process, sensor performance, and environmental conditions that can aid in data interpretation and decision-making (Cota & Mamede, 2023). For example, metadata about the sensor type and calibration parameters can help assess the accuracy and reliability of the collected data, while metadata about the weather conditions and soil properties can provide context for interpreting the data and adjusting irrigation strategies accordingly (Cota & Mamede, 2023). By incorporating metadata into the data management and analysis pipeline of automated irrigation systems, decision-makers can make more informed and context-aware decisions, leading to improved water use efficiency and crop productivity (Jahanddideh-Tehrani et al., 2021).

"""

write_next_section = """

Use the information provided in the <documents> tags to write the next subsection of the research paper, following these steps:
1. Review the overall intention of the research paper, specified in the <review_intention> tag. Ensure the subsection you write aligns with and contributes to this overall goal.
2. Consider the specific intention for this subsection of the paper, stated in the <section_intention> tag. The content you write should fulfill this purpose. 
3. Use the title provided in the <subsection_title> tag as the heading for the subsection. 
4. Address each of the points specified in the </subsection_point_Point *> tags:
   a) Make a clear case for each point using the text provided in the "point" field.
   b) Support each point with evidence from the research papers listed in the corresponding "papers to support point" field.
   c) When citing a paper to support a point, include inline citations with the author name(s) and year, e.g. (Smith et al., 2020; Johnson and Lee, 2019; Brown, 2018). Cite all papers that strengthen or relate to the point being made.
   d) While making a point and citing the supporting papers, provide a brief explanation in your own words of how the cited papers support the point.
5. Ensure that both of the points from the <subsection_point> tags are fully addressed and supported by citations. Do not skip or combine any points.
6. After addressing the specified points, wrap up the subsection with a concluding sentence or two that ties the points together and relates them back to the <section_intention>.
7. Review the <Previous_sections> of the paper, and ensure that the new subsection you have written fits logically and coherently with the existing content. Add transition sentences as needed to improve the flow.
8. Proofread the subsection to ensure it is clear, concise, and free of grammatical and spelling errors. Maintain a formal academic tone and style consistent with the rest of the research paper.
9. Format the subsection using Markdown, including the subsection heading (using ## or the equivalent for the document), inline citations, and any other formatting needed for clarity and readability.
10. If any information is missing or unclear in the provided tags, simply do your best to write the subsection based on the available information. Do not add any information or make any points not supported by the provided content. Prioritize fully addressing the required points over hitting a specific word count.

The output should be a complete, well-organized, and properly cited subsection ready to be added to the research paper.

Begin your answer with a brief recap of the instructions stating what you will to optimize the quality of the answer. Clearly and briefly state the subsection you'll be working on and the points you'll be addressing. Then proceed to write the subsection following the instructions provided. 

Critical: 
- Do not include a conclusion or summary as the entry is in the middle of the document. Focus on addressing the points and supporting them with evidence from the provided papers. Ensure that the subsection is well-structured, coherent, and effectively contributes to the overall research paper.
- The subsection we are focusing on is: 3.4. Real-Time Data Transmission Protocols and Technologies


"""

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

Field codes (e.g. TITLE, ABS, KEY, AUTH, AFFIL) to restrict searches to specific parts of documents
Boolean operators (AND, OR, AND NOT) to combine search terms
Proximity operators (W/n, PRE/n) to find words within a specified distance - W/n: Finds terms within "n" words of each other, regardless of order. Example: journal W/15 publishing finds articles where "journal" and "publishing" are within two words of each other. - PRE/n: Finds terms in the specified order and within "n" words of each other. Example: data PRE/50 analysis finds articles where "data" appears before "analysis" within three words. - To find terms in the same sentence, use 15. To find terms in the same paragraph, use 50 -
Quotation marks for loose/approximate phrase searches
Braces {} for exact phrase searches
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
"scopus_queries": [
"TITLE-ABS-KEY(("precision agriculture" OR "precision farming") AND ("machine learning" OR "AI") AND "water")",
"TITLE-ABS-KEY((iot OR "internet of things") AND (irrigation OR watering) AND sensor*)",
"TITLE-ABS-Key(("precision farming" OR "precision agriculture") AND ("deep learning" OR "neural networks") AND "water")",
"TITLE-ABS-KEY((crop W/5 monitor*) AND "remote sensing" AND (irrigation OR water*))",
"TITLE("precision irrigation" OR "variable rate irrigation" AND "machine learning")"
]
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
{{ "alex_queries": [
"https://api.openalex.org/works?search=%22precision+irrigation%22+%2B%22soil+moisture+sensors%22+%2B%22irrigation+scheduling%22&sort=relevance_score:desc&per-page=30",
"https://api.openalex.org/works?search=%22machine+learning%22+%2B%22irrigation+management%22+%2B%22crop+water+demand+prediction%22&sort=relevance_score:desc&per-page=30",
"https://api.openalex.org/works?search=%22IoT+sensors%22+%2B%22real-time%22+%2B%22soil+moisture+monitoring%22+%2B%22crop+water+stress%22&sort=relevance_score:desc&per-page=30",
"https://api.openalex.org/works?search=%22remote+sensing%22+%2B%22vegetation+indices%22+%2B%22irrigation+scheduling%22&sort=relevance_score:desc&per-page=30",
"https://api.openalex.org/works?search=%22wireless+sensor+networks%22+%2B%22precision+agriculture%22+%2B%22variable+rate+irrigation%22+%2B%22irrigation+automation%22&sort=relevance_score:desc&per-page=30"
]}}

These example searches demonstrate how to create targeted, effective alex searches. They focus on specific topics, exclude irrelevant results, allow synonym flexibility, and limit to relevant domains when needed. The search terms are carefully selected to balance relevance and specificity while avoiding being overly restrictive.  By combining relevant keywords, exact phrases, and operators, these searches help generate high-quality results for the given topics.
"""


def remove_illegal_characters(text):
    if text is None:
        return ""
    illegal_chars = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")
    return illegal_chars.sub("", str(text))


def get_prompt(template_name, **kwargs):

    prompts = {  # Soom to be deprecated
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

Your task is to generate a set of 5 highly optimized search queries that would surface the most relevant, insightful, and comprehensive set of research articles to shed light on various aspects of the particular point <point_content> which is under subsection <subsection_title>, while keeping the queries tightly focused around the intentions of the <section_title> and <review_intention>.

The queries should:
- Be thoughtfully crafted to return results that directly address the key issues and nuances of the <point_content>
- Demonstrate creativity and variety in their formulation to capture different dimensions of the topic
- Use precise terminology and logical operators to maintain a high signal-to-noise ratio in the results
- Cover a broad range of potential subtopics, perspectives, and article types related to the <point_content>
- Align closely with the stated goals of the <section_title> and <review_intention> to maximize relevance 
- Adhere strictly and diligently to any specific guidance or requirements provided in <search_guidance>. This is critical!

Provide your response strictly in the following JSON format:
{{
    "*_queries": [
        "query_1",
        "query_2",
        "query_3",
        "query_4",
        "query_5"
    ]
}}

** Critical: all double quotes other than the outermost ones should be preceded by a backslash (\") to escape them in the JSON format. Failure to do so will result in an error when parsing the JSON string. **

The  platform will be specified in the search guidance. Replace * with the platform name (e.g., scopus_queries, alex_queries). Each query_n should be replaced with a unique, well-formulated search entry according to the instructions in <search_guidance>. No other text should be included. Any extraneous text or deviation from this exact format will result in an unusable output.
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
        "rank_papers": """
Here is the updated prompt with corrected XML tags:

<instructions>
First, carefully read through the full text of the paper provided under <full_text>. Then, analyze the paper's relevance to the specific point mentioned in <point_focus> within the context of the overall literature review intentions and the specific section and sub-section in which the point is located.

Your analysis should include:

1. A concise summary (3-5 sentences) of the key points of the paper as they relate to the outline point. Include this in the "explanation" field of the JSON.

2. A succinct yet detailed explanation of how the specifics of the paper contribute to addressing the point within the larger context and intent of the literature review. Consider the following factors based on the paper type: relevance, insight, credibility, scope, and recency. Include this in the "relevance_evaluation" field of the JSON.

3. A relevance score between 0 and 1 representing the overall fit of the paper to the outline point and review. Use the following rubric and include the score in the "relevance_score" field of the JSON:

0.9-1.0: Exceptionally relevant - Comprehensively addresses all key aspects of the point with highly insightful, reliable, and up-to-date information. A must-include for the review.
0.8-0.89: Highly relevant - Addresses key issues of the point with novel, credible, and meaningful information. Adds substantial value to the review.
0.7-0.79: Very relevant - Directly informs the point with reliable and valuable information, but may have minor limitations in scope, depth, or recency.
0.6-0.69: Moderately relevant - Provides useful information for the point, but has some notable gaps in addressing key issues or limitations in insight, credibility, or timeliness.
0.5-0.59: Somewhat relevant - Addresses aspects of the point, but has significant limitations in scope, depth, reliability, or value of information. May still be worth including.
0.4-0.49: Marginally relevant - Mostly tangential to the main issues of the point, with information of limited insight, credibility, or meaningfulness. Likely not essential.
0.2-0.39: Minimally relevant - Only briefly touches on the point with information that is of questionable value, reliability, or timeliness. Not recommended for inclusion.
0.0-0.19: Not relevant - Fails to address the point or provide any useful information. Should be excluded from the review.

4. The two most relevant verbatim quotes from the paper, each no more than 3 sentences, demonstrating its pertinence to the outline point and review. Include the most important quote under "extract_1" and the second most important under "extract_2". If no quotes are directly relevant, leave these blank. Use quotation marks around the extracts in the JSON.

5. List any important limitations of the paper for fully addressing the point and outline, such as limited scope, methodological issues, dated information, or tangential focus. If there are no major limitations, leave this blank. Include this in the "limitations" field of the JSON as a comma-separated list.

6. Provide a suggested in-line citation for the paper under "inline_citation" in the format (Author, Year), and a full APA style reference under "apa_citation".

7. Under "study_location", provide the specific city/region and country where the study was conducted. If not explicitly stated, infer the most likely location based on author affiliations or other context clues. If the location cannot be determined, write "Unspecified".

8. For "main_objective", state the primary goal or research question of the study in 1-2 sentences.

9. List the key technologies, methods, or approaches used in the study under "technologies_used", separated by commas.

10. Under "data_sources", list the primary sources of data used in the analysis, such as "Survey data", "Interviews", "Case studies", "Literature review", etc. Separate each source with a comma.

11. Summarize the main findings or results of the study in 2-3 sentences under "key_findings".

Provide your analysis in the following JSON format. Be as precise, specific, and concise as possible in your responses. Use the provided fields and format exactly as shown below:

<response_format>
{{
 "explanation": "From your close reading of the paper, provide a concise explanation of the study's purpose and main objectives, using a maximum of 3 sentences.",
 "relevance_evaluation": "Evaluate the relevance of the paper to the specific point you are making in your literature review. Explain your reasoning in a maximum of 3 sentences.",
 "relevance_score": "On a scale from 0.0 to 1.0, parsimoniously rate the relevance of the paper to the point you are making in your review, with 1.0 being the most relevant.",
 "extract_1": "Select the most relevant verbatim quote from the paper that supports your point, using a maximum of 3 sentences.",
 "extract_2": "Select the second most relevant verbatim quote from the paper that supports your point, using a maximum of 3 sentences.",
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

Leave any fields blank if not applicable, but keep the field names. The "explanation" field should be one paragraph maximum.
</instructions>

<context>

<review_intention>
{review_intention}
</review_intention>

<section_intention>
{section_intention}
</section_intention>

<subsection_title>
{subsection_title}
</subsection_title>

<point_focus>
{point_content}
</point_focus>

<full_text>
{full_text}
</full_text>

</context>
""",
    }

    try:
        return prompts[template_name].format(**kwargs)

    except KeyError as e:
        missing_key = str(e).strip("'")
        raise ValueError(
            f"Missing argument for template '{template_name}': {missing_key}"
        )
