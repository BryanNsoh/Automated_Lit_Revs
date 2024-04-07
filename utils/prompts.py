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

3.2. Edge Computing and Fog Computing
Edge computing and fog computing have emerged as transformative technologies in the realm of real-time irrigation management systems, offering significant potential for improving efficiency, scalability, and reliability (Abdel Nasser et al., 2020; Tran et al., 2019). Edge computing refers to the practice of processing data near the edge of the network, close to the source of the data, while fog computing is a decentralized computing infrastructure that extends cloud computing capabilities to the network edge (Hassija et al., 2019). These technologies bring computation and analytics closer to the data source, reducing the need for data to travel to the cloud and enabling faster processing and decision-making (Hassija et al., 2019; Zhang et al., 2020).
The potential of edge computing and fog computing in real-time irrigation management is immense. Abdel Nasser et al. (2020) proposed a two-layer system for water demand prediction using automated meters and machine learning techniques, demonstrating the potential of edge computing in improving the efficiency and scalability of irrigation management. The system collects and aggregates data from distributed smart meters in the first layer, while the second layer uses LSTM neural networks to predict water demand for different regions of households. By leveraging edge computing, the system can achieve high accuracy in predicting water demand, which is essential for efficient irrigation management (Abdel Nasser et al., 2020).
Tran et al. (2019) conducted a comprehensive review of real-time, end-to-end automated irrigation management systems, highlighting the role of fog computing in addressing data transmission challenges and enabling seamless integration across the irrigation management pipeline. The authors emphasize that real-time, end-to-end automated irrigation management systems have the potential to significantly improve water efficiency, crop yields, and reduce labor costs. However, they also identify several challenges that need to be addressed, such as data quality, scalability, reliability, and security, which can be effectively tackled by implementing fog computing architectures (Tran et al., 2019).
Edge computing offers several benefits in real-time irrigation management systems, including reduced latency, real-time decision-making, and reduced reliance on cloud connectivity (Mishra, 2020; Zhang et al., 2020). By processing data closer to the source, edge computing enables faster response times and more efficient data handling (Mishra, 2020). Mishra (2020) highlights that edge computing reduces latency by processing data closer to the source, enabling real-time decision-making and lessening reliance on cloud connectivity by shifting processing to local or edge devices.
Zhang et al. (2020) explore the application of edge computing in agricultural settings, demonstrating its potential to improve the efficiency and accuracy of irrigation systems. The authors discuss how edge computing has prospects in various agricultural applications, such as pest identification, safety traceability of agricultural products, unmanned agricultural machinery, agricultural technology promotion, and intelligent management. They also emphasize that the emergence of edge computing models, such as fog computing, cloudlet, and mobile edge computing, has transformed the management and operation of farms (Zhang et al., 2020).
Fog computing plays a crucial role in distributing processing and storage across the network, enhancing the scalability and reliability of automated irrigation systems (Premkumar & Sigappi, 2022; Singh et al., 2022). Premkumar and Sigappi (2022) evaluate the current state of automated irrigation management systems and propose a hybrid machine learning approach for predicting soil moisture and managing irrigation. Their study emphasizes the potential of fog computing in distributing processing and storage across the network, improving the efficiency and scalability of irrigation systems. The proposed hybrid machine learning approach outperforms other machine learning algorithms in predicting soil moisture, demonstrating the effectiveness of fog computing in enhancing the performance of automated irrigation systems (Premkumar & Sigappi, 2022).
Singh et al. (2022) discuss the role of fog computing in distributing processing and storage across the network, enhancing scalability and reliability in agricultural management systems. The authors argue that by implementing fog computing, these systems can achieve faster data processing and response times, improving overall efficiency and effectiveness. They also highlight that fog computing can address the challenges faced by real-time data transmission in agricultural management systems, such as latency, bandwidth limitations, and data security (Singh et al., 2022).
The integration of edge and fog computing in real-time irrigation management systems is crucial for achieving fully automated, scalable, and reliable solutions. As the demand for autonomous irrigation management grows, these technologies will play a pivotal role in enabling faster decision-making, reduced latency, improved resource utilization, and seamless integration across the irrigation management pipeline (Tran et al., 2019; Zhang et al., 2020). By bringing computation and analytics closer to the data source and distributing processing and storage across the network, edge and fog computing can significantly enhance the efficiency and effectiveness of automated irrigation systems, contributing to the overall goal of addressing the global food challenge through optimized water resource management and increased agricultural productivity (Abdel Nasser et al., 2020; Premkumar & Sigappi, 2022; Singh et al., 2022).

3.3. Automation of Data Collection
The automation of data collection is a critical component in the development of real-time, end-to-end automated irrigation management systems that integrate IoT and machine learning technologies. It enables the efficient gathering of vital information about crop health, environmental conditions, and water requirements, which is essential for enhancing agricultural water use efficiency and crop productivity. Two key aspects of automated data collection are the use of advanced sensing technologies for non-invasive plant stress detection and the implementation of wireless sensor networks and energy-efficient communication protocols for large-scale, long-term data collection.
Advanced sensing technologies, such as hyperspectral imaging and thermal sensing, have emerged as powerful tools for non-invasive plant stress detection in automated irrigation management systems. These technologies provide valuable information about crop traits, enabling early and accurate detection of plant health issues (Triantafyllou et al., 2019). Triantafyllou et al. (2019) propose a comprehensive reference architecture model that incorporates advanced sensing technologies in the sensor layer for real-time plant stress detection, highlighting their importance in providing non-invasive plant stress detection. Similarly, Hossain et al. (2023) present a novel IoT-ML-Blockchain integrated framework for smart agricultural management that leverages advanced sensing technologies to optimize water use and improve crop yield, contributing to the overall goal of enhancing agricultural water use efficiency and crop productivity.
Hyperspectral imaging can capture subtle changes in plant physiology that are indicative of stress, while machine learning algorithms can be employed to extract meaningful patterns from the spectral data and classify different stress types (Araus et al., 2014). Thermal sensing can detect changes in canopy temperature, which is influenced by factors such as plant water status (Li et al., 2019). By monitoring canopy temperature and comparing it to reference values, automated irrigation systems can detect plant water stress and trigger irrigation events to maintain optimal plant health and productivity (Li et al., 2019).
The integration of advanced sensing technologies in automated irrigation management systems has the potential to revolutionize precision agriculture. Jiang et al. (2019) demonstrate the effectiveness of a deep learning-based model in accurately detecting leaf spot diseases, highlighting the importance of image augmentation and deep learning algorithms in enhancing the model's performance.
Wireless sensor networks (WSNs) and energy-efficient communication protocols have the potential to significantly improve the efficiency and reliability of data collection in large-scale, long-term irrigation systems. WSNs offer a cost-effective and scalable solution for real-time data collection in large-scale irrigation systems, providing remote monitoring and automated control capabilities (Mehdizadeh et al., 2020). Nishiura and Yamamoto (2021) propose a novel sensor network system that utilizes drones and wireless power transfer to autonomously collect environmental data from sensor nodes in vast agricultural fields, reducing operational costs and enhancing the efficiency of data collection. Similarly, Higashiura and Yamamoto (2021) introduce a network system that employs UAVs and LoRa communication to efficiently collect environmental data from sensor nodes distributed across large farmlands, optimizing data collection and reducing travel distance and time.
Energy-efficient communication protocols are crucial for ensuring reliable data transmission in challenging environmental conditions and extending the lifespan of sensor nodes (Mehdizadeh et al., 2020). Al-Ali et al. (2023) investigate the potential of WSNs and energy-efficient communication protocols for data collection in large-scale, long-term irrigation systems, discussing the challenges and opportunities of using these technologies to improve the efficiency and reliability of real-time data collection in irrigation management. Mehdizadeh et al. (2020) emphasize the need for careful consideration of factors such as data accuracy, energy consumption, and network reliability when designing effective WSNs for irrigation management, enabling timely irrigation decisions and improved crop yields.
The automation of data collection through the use of advanced sensing technologies and wireless sensor networks is essential for achieving fully autonomous, scalable irrigation management. By enabling non-invasive plant stress detection and large-scale, long-term data collection, these technologies contribute to the overall goal of optimizing water resource management and increasing agricultural productivity. The integration of these technologies in real-time, end-to-end automated irrigation management systems has the potential to enhance agricultural water use efficiency and crop productivity, ultimately contributing to the development of fully autonomous, scalable irrigation management solutions.

3.4: Real-Time Data Transmission Protocols and Technologies
Real-time data transmission is a critical component of automated irrigation management systems, as it enables the timely delivery of sensor data to the cloud for processing and decision-making. The exploration of suitable protocols and network architectures is essential for ensuring efficient and reliable data transmission in these systems, contributing to the overall goal of enhancing agricultural water use efficiency and crop productivity.
The Message Queuing Telemetry Transport (MQTT) protocol has emerged as a popular choice for real-time data transmission in IoT networks, including those used for automated irrigation management. MQTT is a lightweight, publish-subscribe protocol designed for constrained devices and low-bandwidth networks (Author, 2019). Its simplicity and low overhead make it well-suited for IoT applications where data transmission speed and energy efficiency are critical (Saranyadevi et al., 2022). MQTT provides three Quality of Service (QoS) levels, ensuring data reliability in real-time scenarios (Author, 2019). Chen et al. (2020) proposed novel algorithms to improve data exchange efficiency and handle rerouting in MQTT-based IoT networks for automated irrigation management systems. Their TBRouting algorithm efficiently finds the shortest paths for data transmission, while the Rerouting algorithm effectively handles the rerouting of topic-based session flows when a broker crashes. The combination of these algorithms can significantly improve the performance and reliability of automated irrigation management systems (Chen et al., 2020).
Client-server IoT networks, such as those based on MQTT, play a crucial role in real-time data transmission for automated irrigation management systems. In these networks, sensors and devices (clients) publish data to a central broker (server), which then distributes the data to subscribed clients (Verma et al., 2021). This architecture enables efficient data collection, processing, and dissemination, facilitating the integration of various components within the automated irrigation management pipeline. Verma et al. (2021) proposed an architecture for healthcare monitoring systems using IoT and communication protocols, which provides a comprehensive overview of existing approaches and highlights challenges and opportunities in the field. Although focused on healthcare, the insights from this study can be applied to automated irrigation management systems, emphasizing the importance of interoperability and standardization for seamless integration (Verma et al., 2021).
In addition to MQTT, other application layer protocols such as XMPP, CoAP, SOAP, and HTTP have been explored for real-time data transmission in IoT networks. Each protocol has its strengths and weaknesses, making them suitable for different applications and scenarios. XMPP (Extensible Messaging and Presence Protocol) is an open-standard protocol that supports real-time messaging, presence, and request-response services (Saint-Andre, 2011). CoAP (Constrained Application Protocol) is a specialized web transfer protocol designed for use with constrained nodes and networks in the Internet of Things (Shelby et al., 2014). SOAP (Simple Object Access Protocol) is a protocol for exchanging structured information in the implementation of web services, while HTTP (Hypertext Transfer Protocol) is the foundation of data communication for the World Wide Web (Fielding et al., 1999).
Motamedi and Villányi (2022) compared and evaluated wireless communication protocols for the implementation of smart irrigation systems in greenhouses, considering factors such as power consumption, range, reliability, and scalability. They found that ZigBee is the most suitable local communication protocol for greenhouse irrigation due to its large number of nodes and long range, while MQTT is the recommended messaging protocol for smart irrigation systems due to its TCP transport protocol and quality of service (QoS) options. GSM is a reliable and cost-effective global communication protocol for greenhouse irrigation, providing wide coverage and low cost (Motamedi & Villányi, 2022).
Syafarinda et al. (2018) investigated the use of the MQTT protocol in a precision agriculture system using a Wireless Sensor Network (WSN). They found that MQTT is suitable for use in IoT applications due to its lightweight, simple, and low bandwidth requirements. The average data transmission speed using the MQTT protocol was approximately 1 second, demonstrating its effectiveness for real-time data transmission in precision agriculture systems (Syafarinda et al., 2018).
The choice of application layer protocol for real-time irrigation management depends on factors such as data transmission speed, reliability, and energy efficiency. MQTT and RTPS (Real-Time Publish-Subscribe) are both suitable for real-time data transmission in IoT systems, but they have different strengths and weaknesses. MQTT is a better choice for applications that require low latency and high throughput, while RTPS is a better choice for applications that require high reliability and low latency (Sanchez-Iborra & Skarmeta, 2021). The exploration of MQTT and client-server IoT networks, along with the comparison of various application layer protocols, provides valuable insights into the suitability of these technologies for real-time data transmission in automated irrigation management systems.
In summary, real-time data transmission protocols and technologies play a vital role in the automation of irrigation management systems, enabling the efficient and reliable delivery of sensor data to the cloud for processing and decision-making. The exploration of MQTT and client-server IoT networks, along with the comparison of application layer protocols, highlights the importance of selecting suitable technologies based on factors such as data transmission speed, reliability, and energy efficiency. By leveraging these technologies, automated irrigation management systems can achieve seamless integration and contribute to the overall goal of enhancing agricultural water use efficiency and crop productivity.

3.5. Challenges and Solutions in Real-Time Data Transmission
Following the exploration of data collection, processing at the edge and fog, and automation in previous sections, we now turn to the critical aspect of real-time data transmission. While essential for automated irrigation management, this stage presents unique challenges that must be addressed to ensure system efficiency and reliability.
Obstacles in Real-Time Data Transmission
Agricultural environments present unique challenges for real-time data transmission, directly impacting the effectiveness of automated irrigation systems. Environmental factors can significantly disrupt wireless communication. Adverse weather conditions such as heavy rain, fog, and high winds can weaken or even block radio signals, leading to data loss and compromised system performance. Physical obstacles like trees, buildings, and uneven terrain further complicate signal propagation, creating reliability issues (Jukan et al., 2017; Yi & Ji, 2014; Zhang, Chang & Baoguo, 2018). These environmental challenges necessitate robust communication protocols and network architectures that can ensure consistent and reliable data flow.
In addition to environmental factors, technical limitations also present significant obstacles. Large-scale agricultural operations often demand long-distance data transmission, which can be hindered by the limited range of certain wireless communication protocols. Network congestion, occurring when multiple sensors transmit data concurrently, can lead to delays and potential data loss, further complicating real-time decision-making (Hameed et al., 2020). To mitigate these issues, researchers have investigated the potential of cognitive radio networks (CRNs) and dynamic spectrum access (DSA) for optimizing spectrum utilization and reducing interference (Righi et al., 2017; Shafi et al., 2018; Trigka & Dritsas, 2022). CRNs enable devices to intelligently sense and adapt to the surrounding radio environment, dynamically adjusting transmission parameters to avoid interference and improve communication efficiency. DSA, on the other hand, facilitates the dynamic allocation of unused spectrum, enhancing spectrum utilization and reducing congestion.
Furthermore, data security and privacy are paramount concerns in real-time irrigation systems. The sensitive nature of agricultural data, such as crop yields and farm management practices, necessitates robust security measures to prevent unauthorized access and data breaches (Gupta et al., 2020). Implementing secure communication protocols, authentication mechanisms, and encryption techniques is essential to protect data integrity and ensure the trustworthiness of the system.
Investigating Data Optimization Techniques
To enhance the efficiency and reliability of real-time data transmission in automated irrigation systems, researchers have explored a range of data optimization techniques. Data compression techniques aim to reduce the size of data packets transmitted over the network, minimizing bandwidth requirements and improving transmission speed (Rady et al., 2020; Karim et al., 2023). Lossless compression algorithms, such as Huffman coding and LZW, preserve data integrity while effectively reducing data size, ensuring that no information is lost during transmission (Cui, 2023). Lossy compression algorithms, such as JPEG and MP3, offer higher compression ratios but introduce a controlled level of data loss, which may be acceptable for certain applications where some loss of precision is tolerable (Karim et al., 2023). The choice between lossless and lossy compression depends on the specific application and the trade-off between data size and accuracy.
Data aggregation techniques provide another effective approach to optimize data transmission. By aggregating multiple sensor readings into a single representative value, such as average soil moisture or temperature, the number of transmissions can be significantly reduced, conserving bandwidth and energy resources (Cui, 2023). This is particularly beneficial in large-scale irrigation systems where numerous sensors are deployed across vast areas, generating substantial amounts of data. Additionally, data filtering techniques play a crucial role in improving data quality and reliability. Kalman filters and particle filters can effectively remove noise and outliers from sensor data, ensuring that only accurate and relevant information is transmitted and used for decision-making (Cui, 2023). This is essential for preventing erroneous data from influencing irrigation decisions and potentially leading to suboptimal water management.
Sensor calibration, drift correction, and fault detection are essential for maintaining data accuracy and reliability (Dos Santos et al., 2023). Regular calibration ensures that sensors provide accurate measurements over time, while drift correction techniques account for gradual changes in sensor readings due to environmental factors or aging. Fault detection mechanisms can identify and address sensor malfunctions or anomalies, preventing erroneous data from influencing irrigation decisions and potentially harming crops or wasting water.
Addressing the Challenges
Effectively addressing the challenges in real-time data transmission requires a multifaceted approach that encompasses environmental, technical, and data-related considerations. Implementing robust and adaptive communication protocols is crucial for overcoming interference and signal degradation caused by weather conditions and physical obstacles. Selecting appropriate protocols, such as LoRa or ZigBee, with suitable range and penetration capabilities can ensure reliable data transmission in challenging agricultural environments (Motamedi & Villányi, 2022). Additionally, employing techniques like frequency hopping and error correction codes can further improve communication resilience and mitigate data loss.
Optimizing network architecture is another key consideration. Deploying a distributed network architecture with edge and fog computing capabilities can significantly enhance data processing and transmission efficiency (Abdel Nasser et al., 2020; Tran et al., 2019). Edge devices can perform initial data processing and aggregation tasks, reducing the amount of data transmitted to the cloud and minimizing latency, while fog nodes can provide additional processing power and storage closer to the data source, enhancing scalability and reliability. This distributed approach alleviates the burden on the central cloud server and allows for more responsive and efficient irrigation management.
Data optimization techniques play a vital role in reducing bandwidth requirements and improving transmission efficiency. The choice of data compression, aggregation, and filtering techniques should be tailored to the specific requirements of the irrigation system, considering factors such as data type, accuracy needs, and available bandwidth. By carefully selecting and implementing these techniques, the overall performance and effectiveness of real-time irrigation systems can be significantly enhanced, leading to more sustainable water management practices and improved agricultural productivity.
By addressing these challenges and implementing appropriate solutions, real-time data transmission can become a reliable and efficient component of automated irrigation systems, contributing to the overall goal of achieving sustainable and productive agriculture in the face of growing food demands and water scarcity.

3.6. IoT Network Architectures and Variable Rate Irrigation (VRI) for Real-Time Irrigation
Real-time irrigation management systems heavily rely on the efficient and reliable transmission of data from sensors and weather stations to the cloud for processing and decision-making. However, agricultural environments present unique challenges to wireless communication, including adverse weather conditions, physical obstacles, and the limitations of wireless technologies. These challenges necessitate robust and adaptive solutions to ensure the consistent and timely flow of data, enabling truly autonomous irrigation scheduling.
Environmental factors, such as heavy rain, fog, and strong winds, can significantly disrupt wireless communication by attenuating or even blocking radio signals, leading to data loss and compromised system performance (Ed-daoudi et al., 2023; Jukan et al., 2017; Yi & Ji, 2014; Zhang, Chang & Baoguo, 2018). Dense vegetation, buildings, and uneven terrain create further complications by causing multipath propagation and shadowing effects (Yim et al., 2018; Gautam and Pagay, 2020). The study by Yim et al. (2018) on LoRa networks in a tree farm environment exemplifies these challenges, revealing reduced communication range and data reliability compared to theoretical expectations. This underscores the need for carefully selecting and optimizing communication protocols and network parameters to ensure reliable data transmission in such environments.
The study by Guzinski et al. (2014a) using a modified TSEB model further highlights the importance of high-resolution data in accurately capturing the spatial and temporal dynamics of energy fluxes influenced by environmental factors. This emphasizes the need for advanced data acquisition and processing techniques that can effectively represent the complexities of agricultural settings.
The limitations of traditional wireless communication technologies, such as limited range and network congestion, pose additional challenges for large-scale agricultural operations. Long-distance data transmission can be hindered by range limitations, while network congestion arising from numerous sensors transmitting concurrently can lead to delays and data loss, hindering real-time decision-making (Hameed et al., 2020). Addressing these challenges requires the exploration of advanced networking technologies that can optimize spectrum utilization, mitigate interference, and improve reliability and efficiency.
Cognitive Radio Networks (CRNs) and Dynamic Spectrum Access (DSA) offer promising solutions for optimizing wireless communication in agricultural settings. CRNs empower devices with the ability to intelligently sense and adapt to the surrounding radio environment, dynamically adjusting transmission parameters to avoid interference and improve communication efficiency (Righi et al., 2017; Shafi et al., 2018; Trigka & Dritsas, 2022). Research has explored the potential of CRNs in predicting Radio Frequency (RF) power to avoid noisy channels and optimize spectrum utilization (Iliya et al., 2014; Iliya et al., 2014). These studies demonstrate the effectiveness of combining optimization algorithms with artificial neural networks (ANNs) to enhance the accuracy and generalization of RF power prediction, enabling CRNs to make informed decisions about channel selection and avoid interference.
DSA complements CRN technology by dynamically allocating unused spectrum, further enhancing spectrum utilization and reducing congestion (Shi et al., 2023). The numerical model developed by Shi et al. (2023) showcases the potential of CRNs and DSA for optimizing wireless communication in challenging environments.
The integration of CRNs and DSA into the IoT network architecture requires careful consideration of spectrum sensing techniques, network topology, and data security. Research on cooperative spectrum sensing suggests that distributed approaches, where sensor nodes collaborate and share information, can significantly improve the accuracy and efficiency of spectrum sensing, particularly in dynamic environments (Trigka and Dritsas, 2022; Khalid & Yu, 2019). This collaborative approach enables a more comprehensive understanding of the radio environment and facilitates the identification of available frequency bands for data transmission.
The choice of network topology also impacts the performance and scalability of CRN-based irrigation systems. Mesh networks, where sensor nodes are interconnected and relay data for each other, offer enhanced resilience and coverage compared to star topologies where nodes communicate directly with a central gateway (Akyildiz & Vuran, 2010). However, mesh networks can be more complex to manage and may introduce additional routing overhead. The trade-off between network resilience and complexity needs to be carefully evaluated to select the most appropriate topology for a specific agricultural setting.
Data security and privacy are paramount concerns in IoT-based irrigation systems due to the sensitive nature of agricultural data (Gupta et al., 2020). Implementing secure communication protocols, authentication mechanisms, and encryption techniques is essential for protecting data integrity and ensuring system trustworthiness. Research on secure spectrum leasing and resource allocation algorithms for CR-WSN-based irrigation systems has demonstrated the potential of these technologies for enhancing security and efficiency (Hassan, 2023; Afghah et al., 2018).
In conclusion, the development of effective and reliable real-time irrigation management systems requires a comprehensive approach that addresses the challenges of data transmission in agricultural environments. The integration of robust and adaptive communication protocols, optimized network architectures, and advanced networking technologies like CRNs and DSA, along with a focus on data security and privacy, can contribute significantly to achieving the goal of autonomous and efficient irrigation scheduling.
4. AUTOMATED DATA PROCESSING IN THE CLOUD
4.1. Data Quality and Preprocessing
Data quality is paramount in automated irrigation systems as it directly influences the effectiveness of decision-making and water use efficiency. Issues like missing values, inconsistencies, and outliers arising from sensor malfunctions, environmental interference, or network problems (Lv et al., 2023) can significantly impact the performance of machine learning models used for irrigation scheduling and management.
Real-time data cleaning techniques are essential for addressing these challenges. Kalman filtering proves particularly effective in handling missing values and correcting erroneous readings by recursively estimating the system's state based on previous measurements and current sensor data, taking into account noise and uncertainty (Kim et al., 2020). Moving average techniques, by averaging consecutive data points, provide a more stable representation of the underlying trend, filtering out short-term fluctuations (Chhetri, 2023). For outlier detection, adaptive thresholding methods offer a dynamic approach, adjusting thresholds based on the statistical properties of the data to effectively identify anomalies and minimize false positives (Bah et al., 2021). These techniques are crucial in maintaining the integrity of real-time data streams and ensuring the accuracy of subsequent analyses.
Adaptive data preprocessing is essential for managing the diversity of data sources and formats commonly found in irrigation systems. Data normalization techniques, such as min-max scaling or z-score normalization, ensure that all features contribute equally to the analysis by transforming data values to a common scale (Pradal et al., 2016). This is crucial for preventing features with larger values from dominating the analysis and ensuring that all features are given equal consideration. Similarly, feature scaling methods, like standardization or normalization, optimize the range of feature values to improve the performance and convergence of machine learning models (Tortorici et al., 2024). By scaling features to a similar range, the influence of outliers is reduced, and the model's ability to learn from the data is enhanced.
Data fusion techniques play a critical role in integrating information from diverse sources, creating a more comprehensive and reliable dataset for irrigation management. Dempster-Shafer theory, a generalization of probability theory, allows for the expression of both uncertainty and the degree of conflict in evidence, making it suitable for fusing uncertain and conflicting data from heterogeneous sources (Sadiq and Rodriguez, 2004). This is particularly relevant in irrigation systems where data from different sensors may provide slightly different or even contradictory information due to sensor variations or environmental factors. Bayesian inference offers another powerful framework for combining information from multiple sources, updating the probability of a hypothesis as new evidence becomes available. By applying these techniques, data from soil moisture sensors, canopy temperature sensors, weather stations, and other sources can be integrated to provide a holistic understanding of crop water requirements and environmental conditions, leading to more informed and accurate irrigation decisions.
The impact of data quality extends beyond model accuracy to the robustness of machine learning models under varying conditions. Robust models should maintain consistent performance even when faced with data inconsistencies or unexpected situations. Techniques like data augmentation and domain adaptation can enhance model robustness by exposing the model to a wider range of data variations during training. Data augmentation involves generating additional training data by applying transformations or introducing noise to existing data, making the model more resilient to noise and variations in the real-world data. Domain adaptation techniques aim to adapt a model trained on one domain (e.g., a specific crop or geographic location) to perform well on another domain with different data characteristics. This is particularly relevant in irrigation management, where models may need to be applied to different crops, soil types, or climatic conditions.
The choice of data cleaning, preprocessing, and fusion techniques should be carefully considered based on the specific characteristics of the irrigation system and the available data. By selecting and implementing appropriate techniques, the accuracy, reliability, and robustness of machine learning models can be significantly improved, leading to more efficient and sustainable irrigation management practices.
4.2. Scalable and Autonomous Deployment using Containerization Strategies
The transition from data collection and transmission to efficient data processing requires a robust infrastructure capable of handling diverse workloads and data volumes. Containerization technologies, specifically Docker and Kubernetes, offer a promising solution for deploying and scaling data processing and machine learning modules within cloud environments like AWS, Azure, and GCP (Vargas-Rojas et al., 2024; Rosendo et al., 2022; Solayman & Qasha, 2023). Docker provides a standardized way to package applications and their dependencies into self-contained units known as containers, ensuring consistent and reproducible execution across different platforms (Rosendo et al., 2022). Kubernetes, acting as a container orchestrator, manages their deployment, scaling, and networking across a cluster of machines (Rosendo et al., 2022). This combination presents several advantages for automated irrigation management systems.
Firstly, containerization facilitates efficient resource utilization and scalability. By encapsulating applications and their dependencies, containers enable the isolation of resources and prevent conflicts between different modules (Vargas-Rojas et al., 2024; Solayman & Qasha, 2023). This isolation allows for the efficient allocation of resources, such as CPU, memory, and storage, to each container based on its specific needs. Kubernetes further enhances scalability by allowing for the automatic scaling of containers based on real-time demand, ensuring the system can adapt to varying workloads and data volumes, preventing bottlenecks, and ensuring responsiveness to changing conditions (Karamolegkos et al., 2023).
Secondly, containerization promotes portability and reproducibility. By packaging applications and their dependencies into a single unit, containers make it easy to move and deploy them across different cloud environments without the need for environment-specific configurations (Rosendo et al., 2022; Solayman & Qasha, 2023). This portability simplifies the development and deployment process, reducing the time and effort required to set up and manage the system. Additionally, containers ensure reproducibility by providing a consistent execution environment, regardless of the underlying infrastructure. This eliminates variability and ensures that the system will behave consistently across different deployments (Zhou et al., 2023).
Optimizing container orchestration and resource allocation is crucial to minimizing latency and maximizing throughput in real-time data processing pipelines. Techniques like auto-scaling and dynamic resource allocation play a critical role in this context (Hethcoat et al., 2024; Werner and Tai, 2023; Kumar et al., 2024). Auto-scaling automatically adjusts the number of container instances based on real-time demand, ensuring that sufficient resources are available to handle peak workloads while avoiding over-provisioning during periods of low demand (Hethcoat et al., 2024; Kumar et al., 2024). Dynamic resource allocation enables the fine-grained adjustment of resources allocated to each container based on its specific needs and the current workload (Werner and Tai, 2023). This ensures efficient resource allocation and provides each container with the necessary resources to perform its tasks effectively.
Performance monitoring tools, such as Kubernetes Metrics Server and Prometheus, are essential for gaining insights into the performance of containers and the overall system (Hethcoat et al., 2024; Kuity & Peddoju, 2023). These tools provide valuable data on key performance indicators, such as CPU and memory usage, network traffic, and application-specific metrics. By monitoring this data, administrators can identify bottlenecks, optimize resource allocation strategies, and continuously improve system performance (Hethcoat et al., 2024). This data-driven approach ensures that automated irrigation management systems can operate efficiently and reliably.
By integrating containerization technologies with optimization techniques and performance monitoring, automated irrigation management systems achieve the scalability, autonomy, and efficiency required for effective real-time data processing and decision-making. This approach facilitates a seamless and responsive system that can adapt to changing conditions and contribute to the overall goal of optimizing water resource management and increasing agricultural productivity.

4.3. Deploying ML Models for Data Processing
Transitioning from data collection, preprocessing, and transmission, the deployment of machine learning (ML) models marks a pivotal stage in the automated irrigation management pipeline. This stage entails utilizing cloud platforms to facilitate real-time data processing and inference, enabling data-driven decision-making for optimal irrigation management and ultimately contributing to fully autonomous, scalable irrigation management.
Several architectures and frameworks exist for deploying ML models on cloud platforms, each offering unique advantages and catering to different requirements. TensorFlow Serving, for instance, provides a high-performance system specifically designed for serving TensorFlow models (Abadi et al., 2016). This framework enables efficient and scalable inference, making it suitable for real-time applications where low latency and high throughput are crucial. For instance, in a large-scale irrigation system with numerous sensors generating data continuously, TensorFlow Serving can efficiently handle the high volume of inference requests and provide timely predictions for irrigation scheduling. Similarly, Apache MXNet Model Server offers a flexible and efficient solution for deploying models trained with MXNet, supporting a wide range of deep learning models and inference backends (MXNet Developers, 2015). This versatility makes it suitable for complex irrigation systems that may utilize different types of ML models for various tasks, such as predicting crop water requirements, detecting plant stress, or forecasting weather conditions. ONNX Runtime, on the other hand, provides a cross-platform inference engine compatible with various ML frameworks, including PyTorch, TensorFlow, and MXNet (Microsoft, 2017). This versatility enables the deployment of models in diverse environments, facilitating interoperability and reducing the need for model conversion. For example, an irrigation system that uses models trained in different frameworks can utilize ONNX Runtime to deploy them on a single platform without the need for time-consuming and error-prone model conversion processes.
Choosing the appropriate architecture or framework depends on several factors, including the specific ML framework used for model training, the desired level of performance and scalability, and the need for cross-platform compatibility. For instance, if the primary concern is low latency and high throughput for real-time inference, TensorFlow Serving might be the optimal choice for TensorFlow models. However, if flexibility and support for various deep learning models are required, Apache MXNet Model Server could be more suitable. In cases where cross-platform compatibility is essential, ONNX Runtime offers a versatile solution.
Once the ML model is deployed, optimizing its performance and resource utilization becomes crucial for ensuring the efficiency of integrated end-to-end automated irrigation systems. Model compression techniques, such as pruning and quantization, offer effective methods for reducing the size and computational requirements of ML models without compromising accuracy (Premkumar & Sigappi, 2022). Pruning involves eliminating unnecessary connections or neurons from the model, effectively streamlining its structure and reducing computational complexity. This can be particularly beneficial for deep learning models, which often have a large number of parameters and can be prone to overfitting. By removing redundant or less important connections, pruning can improve modelgeneralizability and reduce inference time. Quantization, on the other hand, involves reducing the precision of model parameters, typically from 32-bit floating-point numbers to lower-precision formats such as 8-bit integers. This reduction in precision leads to smaller model sizes and faster inference speeds, making it particularly beneficial for resource-constrained environments or real-time applications. For instance, in edge computing scenarios where ML models are deployed on devices with limited computational resources, quantization can enable efficient inference without sacrificing accuracy.
Furthermore, hardware acceleration through the utilization of GPUs or TPUs can significantly enhance model performance by leveraging specialized hardware designed for parallel processing (Premkumar & Sigappi, 2022). GPUs, with their massive parallelism and high memory bandwidth, excel at accelerating matrix operations and convolutions, which are fundamental computations in many deep learning models. This acceleration can significantly reduce inference time and enable real-time processing of sensor data for timely irrigation decisions. TPUs, specifically designed for deep learning workloads, offer even greater performance and energy efficiency for specific model architectures. These hardware accelerators can drastically reduce inference time, enabling near real-time decision-making and enhancing the responsiveness of automated irrigation systems. For example, in a scenario where immediate response to changing weather conditions or soil moisture levels is critical, hardware acceleration can ensure that irrigation decisions are made and executed promptly.
In addition to model compression and hardware acceleration, distributed training techniques play a crucial role in optimizing the training process for large-scale ML models. Techniques such as Horovod and BytePS enable the distribution of training across multiple machines, effectively parallelizing the process and reducing training time (Premkumar & Sigappi, 2022). This is particularly beneficial for complex models with a large number of parameters or when dealing with large datasets. By leveraging distributed training, irrigation management systems can train more sophisticated models and improve their predictive capabilities, leading to more accurate and efficient irrigation decisions. For instance, a system that utilizes a deep learning model with millions of parameters can benefit from distributed training to reduce training time from days to hours, enabling faster model iteration and improvement.
Integrating the deployed ML models with other components of the automated irrigation management pipeline is essential for achieving a fully autonomous and cohesive system and addressing the need for seamless integration across the automated irrigation management system. Standardized protocols, such as MQTT and CoAP, provide lightweight and efficient communication channels for exchanging data between these components (Poojara et al., 2023; Jimenez et al., 2020a; Gour et al., 2023). MQTT, with its publish-subscribe architecture, enables real-time data streaming and event-driven communication, making it suitable for transmitting sensor data, control signals, and inference results (Raikar & M, 2023). This enables the ML model to receive real-time updates on soil moisture, weather conditions, and plant health, allowing for dynamic adjustments to irrigation schedules based on the latest data. CoAP, designed for constrained devices and low-power networks, offers a web-transfer protocol for resource-constrained environments, enabling efficient communication between sensors, actuators, and the ML models (Raikar & M, 2023). This is particularly relevant in situations where sensors or actuators have limited processing power or battery life, as CoAP minimizes communication overhead and energy consumption. Additionally, RESTful APIs provide a standardized interface for accessing and controlling the ML models, enabling seamless integration with other software components and facilitating system management and monitoring (Wang et al., 2022). This allows for easy integration with existing farm management systems or third-party applications, creating a unified platform for comprehensive irrigation management.4.4. Online Learning in the Cloud
The complexities of real-time data processing in irrigation management necessitate the exploration of advanced techniques to continuously learn and adapt to the dynamic nature of agricultural environments. Online learning algorithms offer a promising solution, enabling the continuous update and improvement of machine learning models based on incoming real-time data. This adaptability is crucial for addressing the challenges of changing environmental conditions, such as weather patterns and crop growth stages, and optimizing irrigation decision-making to enhance water usage efficiency and crop productivity.
Several online learning algorithms have demonstrated potential for real-time data processing and model adaptation in the context of irrigation management. Stochastic Gradient Descent (SGD) facilitates the incremental update of model parameters with each new data point, allowing for efficient adaptation to changing data distributions (Bottou, 2010). This incremental learning process ensures that the model remains responsive to the latest conditions, minimizing the risk of outdated predictions and improving the accuracy of irrigation decisions. Passive-Aggressive algorithms, on the other hand, adjust model parameters only when a misclassification occurs, providing a computationally efficient approach for handling large data streams (Crammer et al., 2006). These algorithms offer a robust approach to handling noisy data, a common challenge in real-world sensor readings, by making small adjustments only when the model's prediction deviates significantly from the actual value (Fei et al., 2019). Online Random Forests extend the concept of random forests to the online setting, enabling the incremental construction and update of decision trees as new data arrives (Saffari et al., 2009). The continuous evolution of the ensemble ensures that the model remains relevant to the changing environment, capturing intricate relationships between variables and leading to more informed irrigation decisions.
Research in various domains highlights the importance of online learning for real-time data stream analytics. Snyder et al. (2020) explored the application of online learning techniques for identifying relevant tweets in real-time, improving situational awareness for first responders. The proposed interactive learning framework allows users to continuously label the relevance of incoming tweets, enabling the real-time refinement of the underlying machine learning model. This user-guided approach aligns well with the dynamic nature of irrigation management, where models need to continuously adjust to varying environmental conditions and crop water requirements. Similarly, research in the field of cyber-physical systems (CPS) underscores the need for online learning algorithms to effectively extract insights and knowledge from continuously generated data streams (Fei et al., 2019). These capabilities are crucial for enabling feedback loops between physical processes and cyber elements, facilitating the integration and optimization of CPS in irrigation management systems.
To implement online learning in cloud-based irrigation management systems, various architectures and frameworks can be considered. Apache Spark Streaming, Apache Flink, and AWS Kinesis provide scalable and fault-tolerant platforms for processing real-time data streams, allowing for the development of online learning pipelines that continuously ingest and analyze data to update machine learning models (Zaharia et al., 2012; Carbone et al., 2015; Amazon Web Services, 2023). These frameworks leverage serverless computing paradigms, automatically scaling resources based on the volume and velocity of incoming data, ensuring efficient resource utilization and responsiveness to fluctuations in demand (Fei et al., 2019).
Effectively managing the exploration-exploitation trade-off is crucial for optimizing online learning in irrigation management. Techniques such as Multi-armed bandits (Sutton & Barto, 2018), Bayesian optimization (Shahriari et al., 2016), and Reinforcement Learning (RL) (Sutton & Barto, 2018) can be employed to balance the allocation of resources between exploring new irrigation strategies and exploiting the current best-performing approaches. These techniques enable the identification of optimal irrigation policies, adapting to changing environmental conditions and maximizing long-term rewards.
In conclusion, online learning techniques, coupled with scalable cloud-based architectures, offer a powerful solution for real-time data processing and continuous adaptation in irrigation management systems. By leveraging algorithms like SGD, Passive-Aggressive, and Online Random Forests, along with stream processing frameworks like Apache Spark Streaming, Apache Flink, and AWS Kinesis, irrigation management systems can effectively handle the complexities of real-time data, optimize water usage, and enhance crop productivity in the face of dynamic environmental conditions.

5. GENERATING AND APPLYING IRRIGATION INSIGHTS 
5.1. Real-Time Generation of Actionable Irrigation Insights
•	Advanced predictive models, such as deep learning (e.g., LSTM, CNN) and ensemble methods (e.g., Random Forests), for precise, site-specific irrigation recommendations
•	Integration of IoT sensor data (e.g., soil moisture probes, weather stations) and cloud-based data sources (e.g., weather forecasts, satellite imagery) using data fusion techniques (e.g., Kalman filtering) to enhance insight accuracy and resolution
•	Strategies for handling data heterogeneity, uncertainty, and quality issues in real-time insight generation, such as data preprocessing and outlier detection
•	Techniques for reducing computational complexity and latency, such as edge computing (e.g., fog computing), model compression (e.g., quantization), and hardware accelerators (e.g., GPUs)
5.2. Automated Application of Irrigation Insights
•	Architectures and protocols for seamless integration of ML-generated insights with IoT-enabled irrigation control systems, such as MQTT and CoAP for lightweight, real-time communication
•	Analysis of industry-leading products and services, such as smart irrigation controllers (e.g., Rachio) and cloud-based irrigation management platforms (e.g., CropX)
•	Strategies for ensuring reliability, security, and scalability of automated insight application, such as redundant communication channels and secure edge-to-cloud architectures
•	Case studies of successful implementations of closed-loop, autonomous irrigation systems in research and commercial settings, highlighting technologies used and benefits achieved

6. INTEGRATION, INTEROPERABILITY, AND STANDARDIZATION 
6.1. Interoperability and Standardization
•	Importance of interoperability and standardization in enabling seamless integration of automated irrigation components
•	Overview of existing and emerging standards for IoT devices, communication protocols, and data formats in precision agriculture (e.g., ISOBUS, agroXML, SensorML)
•	Role of standardization bodies and industry consortia in promoting interoperability (e.g., AgGateway, Open Ag Data Alliance, Agricultural Industry Electronics Foundation)
•	Challenges in adopting and implementing standards across diverse hardware and software platforms
•	Strategies for encouraging widespread adoption of standards and best practices for interoperability in automated irrigation systems
6.2. Integration with Existing Irrigation Infrastructure
•	Challenges and strategies for retrofitting legacy irrigation systems with IoT sensors, actuators, and communication devices
•	Hardware compatibility issues and solutions (e.g., adapters, modular designs)
•	Software and firmware updates to enable integration with automated decision-making systems
•	Data integration and normalization techniques for merging legacy and new data sources
•	Economic and practical considerations for transitioning from manual to automated irrigation management
•	Cost-benefit analysis of upgrading existing infrastructure vs. implementing new systems
•	Phased implementation approaches to minimize disruption and optimize resource allocation
•	Training and support requirements for farmers and irrigation managers adopting automated systems
•	Case studies and real-world examples of successful integration of automated irrigation with existing infrastructure
6.3. Integration with Other Precision Agriculture Technologies
•	Synergies between automated irrigation and complementary technologies
•	Remote sensing (satellite, UAV, and ground-based) for crop monitoring and evapotranspiration estimation
•	Soil moisture sensors and weather stations for real-time, localized data collection
•	Variable rate application systems for precise irrigation delivery based on crop requirements
•	Yield mapping and analytics for assessing the impact of automated irrigation on crop productivity
•	Architectures and frameworks for integrating diverse data sources and technologies into a unified precision agriculture ecosystem
•	Edge computing and fog computing paradigms for real-time data processing and decision-making
•	Cloud-based platforms for data storage, analysis, and visualization
•	API-driven approaches for modular integration of third-party services and applications
•	Challenges and solutions for ensuring data quality, consistency, and security across integrated precision agriculture systems
•	Data cleaning, preprocessing, and harmonization techniques
•	Blockchain and distributed ledger technologies for secure, tamper-proof data sharing and traceability
•	Access control and authentication mechanisms for protecting sensitive data and resources
•	Future trends and research directions in the integration of automated irrigation with advanced precision agriculture technologies (e.g., AI-driven crop modeling, robotics, and autonomous vehicles)
6.4. Cybersecurity Considerations for Integrated Automated Irrigation Systems
•	Unique security risks and vulnerabilities associated with IoT-based automated irrigation systems
•	Potential for unauthorized access, data tampering, and system manipulation
•	Implications of security breaches for crop health, water resource management, and farm productivity
•	Best practices and strategies for securing automated irrigation systems
•	Secure device provisioning and authentication (e.g., hardware security modules, certificates)
•	Encryption and secure communication protocols (e.g., TLS, DTLS)
•	Firmware and software updates to address emerging security threats
•	Network segmentation and access control to limit the impact of breaches
•	Role of cybersecurity standards and frameworks in guiding the development and deployment of secure automated irrigation systems (e.g., NIST CSF, IEC 62443)
•	Importance of user awareness, training, and incident response planning in maintaining the security of integrated automated irrigation systems

7. MONITORING AND ENSURING SYSTEM RELIABILITY
7.1. Resilience and Fault Tolerance in Automated Irrigation Systems
•	Strategies for ensuring robustness and reliability in the face of failures, disruptions, or unexpected events
•	Redundancy: Implementing redundant components, such as duplicate sensors (e.g., soil moisture sensors, weather stations), controllers (e.g., PLCs, microcontrollers), and communication channels (e.g., cellular, satellite, LoRaWAN) to maintain system functionality during component failures
•	Failover mechanisms: Designing seamless failover mechanisms that automatically switch to backup components or systems in case of primary system failure, such as hot-standby controllers or multi-path communication protocols (e.g., mesh networks, software-defined networking)
•	Self-healing capabilities: Incorporating AI-driven self-healing mechanisms that can detect, diagnose, and recover from faults without human intervention, using techniques like reinforcement learning, Bayesian networks, or self-organizing maps
•	The role of distributed architectures and edge computing in enhancing system resilience
•	Decentralizing critical functions and data processing to minimize the impact of single points of failure, using fog computing or multi-agent systems
•	Leveraging edge computing to enable localized decision-making and control, reducing dependence on cloud connectivity and improving response times, using technologies like Raspberry Pi, NVIDIA Jetson, or Intel NUC
•	Anomaly detection and predictive maintenance using AI techniques
•	Employing unsupervised learning algorithms (e.g., autoencoders, clustering) to detect anomalies in sensor data, system performance, and water usage patterns
•	Developing predictive maintenance models using techniques like long short-term memory (LSTM) networks, convolutional neural networks (CNNs), or gradient boosting machines (GBMs) to anticipate and prevent potential system failures based on historical data and real-time monitoring
7.2. Advanced Monitoring Techniques for Automated Irrigation Systems
•	Remote monitoring using IoT-enabled sensors and computer vision
•	Deploying a heterogeneous network of IoT sensors to collect real-time data on soil moisture (e.g., capacitive, tensiometric), temperature (e.g., thermocouples, thermistors), humidity (e.g., capacitive, resistive), and plant health (e.g., sap flow, leaf wetness)
•	Integrating high-resolution cameras (e.g., multispectral, hyperspectral) and computer vision algorithms for visual monitoring of crop growth, disease detection (e.g., using deep learning-based object detection and segmentation), and irrigation system performance (e.g., leak detection, sprinkler uniformity)
•	Transmitting sensor and camera data to cloud-based platforms (e.g., AWS IoT, Google Cloud IoT, Microsoft Azure IoT) for remote access and analysis using protocols like MQTT, CoAP, or AMQP
•	Innovative approaches for real-time system health assessment
•	Developing novel algorithms and metrics for evaluating the health and performance of automated irrigation systems, such as entropy-based measures, network resilience indices, or multi-criteria decision analysis (MCDA) frameworks
•	Combining data from multiple sources (e.g., sensors, weather forecasts, satellite imagery) using data fusion techniques (e.g., Kalman filters, Dempster-Shafer theory) to create a comprehensive view of system health
•	Employing advanced data visualization techniques (e.g., interactive dashboards, augmented reality) to present system health information in an intuitive and actionable format
7.3. Closed-Loop Control and Feedback Mechanisms
•	Exploring the concept of closed-loop control in autonomous irrigation systems
•	Implementing feedback loops that continuously monitor system performance and adjust irrigation schedules based on real-time data, using control techniques like proportional-integral-derivative (PID), model predictive control (MPC), or fuzzy logic control (FLC)
•	Integrating machine learning algorithms (e.g., reinforcement learning, genetic algorithms) to optimize closed-loop control strategies over time, adapting to changing environmental conditions and crop requirements
•	Designing effective feedback mechanisms for user interaction and system optimization
•	Providing user-friendly interfaces (e.g., mobile apps, web dashboards) for farmers to input preferences, constraints, and expert knowledge into the automated irrigation system, using techniques like participatory design or user-centered design
•	Incorporating user feedback and domain expertise to refine irrigation strategies and improve system performance
8. CASE STUDIES AND REAL-WORLD IMPLEMENTATIONS OF FULLY AUTONOMOUS IRRIGATION SYSTEMS
8.1. Fully Autonomous Irrigation Systems in Diverse Agricultural Settings
•	Row Crops: maize, wheat, soybean with real-time soil moisture monitoring and weather-based irrigation scheduling for fully automated precision irrigation
•	Orchards: citrus, apple, almond with plant health monitoring and precision water application for fully autonomous orchard management
•	Greenhouses: tomato, lettuce, herbs with automated drip irrigation and climate control integration for fully automated greenhouse operations
•	Urban Farming: rooftop gardens, vertical farms with IoT-enabled hydroponic systems and remote management for fully autonomous urban crop production
8.2. Integration of Advanced System Components for End-to-End Automation
•	Wireless sensor networks: soil moisture probes, weather stations, plant health monitoring cameras with low-power, long-range communication for fully automated data acquisition
•	Secure data transmission: LoRaWAN, NB-IoT, 5G, satellite communication for reliable, real-time data transfer from field to cloud in fully autonomous irrigation systems
•	Intelligent data processing: edge computing for local data filtering, cloud platforms for scalable storage and analysis, machine learning algorithms for predictive insights in fully automated irrigation management
•	Autonomous decision-making: advanced irrigation scheduling algorithms, precise valve control, closed-loop feedback systems for optimal water management in fully autonomous irrigation systems
8.3. Quantitative Performance Evaluation of Fully Automated Irrigation Systems
•	Water use efficiency: percent reduction in water consumption compared to conventional methods, improved water productivity (yield per unit of water) achieved through fully autonomous irrigation
•	Crop yield and quality improvements: percent increase in yield, enhanced crop uniformity, improved nutritional content attributed to fully automated precision irrigation
•	Labor and energy savings: quantified reduction in labor hours for irrigation management, decreased energy consumption for pumping due to optimized scheduling in fully autonomous systems
•	Economic viability: detailed return on investment analysis, payback period calculations, comprehensive cost-benefit analysis for fully autonomous irrigation management systems
8.4. Lessons Learned and Challenges Encountered in Deploying Autonomous Irrigation Systems
•	Technical challenges and solutions: ensuring reliable data transmission in remote locations, addressing interoperability issues between diverse system components, optimizing power consumption for extended battery life, adapting algorithms to local soil and weather conditions in fully autonomous irrigation systems
•	Operational and logistical hurdles: streamlining installation and maintenance procedures, providing effective user training, seamlessly integrating with existing farm management practices and legacy systems for fully automated irrigation management
•	Regulatory and socio-economic considerations: navigating complex water use regulations, addressing data privacy and security concerns, ensuring equitable access and affordability for smallholder farmers adopting fully autonomous irrigation technologies
8.5. Best Practices and Recommendations for Successful Implementation
•	Designing scalable, modular, and adaptable autonomous irrigation systems to accommodate future growth and changing requirements for fully automated water management
•	Prioritizing user-centered design principles and actively engaging stakeholders throughout the development and deployment process of fully autonomous irrigation solutions
•	Adopting open standards and communication protocols to enable seamless integration of system components and interoperability with third-party platforms in fully automated irrigation setups
•	Implementing robust data validation, filtering, and quality control mechanisms to ensure data integrity and reliability for decision-making in fully autonomous irrigation systems
•	Establishing clear data governance policies and security frameworks to protect sensitive information and maintain user trust in fully automated irrigation management
•	Developing intuitive user interfaces and decision support tools to facilitate easy adoption and effective use of fully autonomous irrigation systems
•	Collaborating with local extension services, agribusinesses, and technology providers for knowledge transfer, technical support, and continuous improvement of fully automated irrigation solutions
8.6. Synthesis of Case Studies and Implications for Autonomous Irrigation Adoption
•	Cross-case analysis of key performance indicators and critical success factors for fully autonomous irrigation scheduling systems in various contexts
•	Identification of common themes, challenges, and innovative solutions across diverse implementations of end-to-end fully automated irrigation management
•	Assessment of the potential for replicability and scaling of successful fully autonomous irrigation projects in different regions and farming systems
•	Implications for future research priorities, technology development roadmaps, and policy interventions to support widespread adoption of fully autonomous irrigation technologies

CONCLUSION/FUTURE DIRECTIONS AND UNANSWERED QUESTIONS
•	Summarize the key insights gained from the question-driven review, emphasizing how each section contributes to the overarching goal of achieving real-time, end-to-end automation in irrigation management
•	Based on the questions addressed, propose new research directions and unanswered questions
•	Identify key research gaps and propose concrete research questions and hypotheses for advancing the field of real-time, automated irrigation management
•	Highlight the need for collaborative research efforts across disciplines, such as computer science, agricultural engineering, and environmental science, to address the complex challenges of automated irrigation systems
•	Emphasize the need for further innovation and exploration in real-time, automated irrigation systems



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
- The subsection we are focusing on is: stated in: <subsection_title>
- No need for sub-sub-sections. just provide paragraphs addressing each point. They should transition fluidly and narurally into each other.
- Ensure that the content is supported by the provided papers and that the citations are correctly formatted and placed within the text.
- Do not repeat content from the previous sections. Ensure that the information provided is new and relevant to the subsection being written.


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
