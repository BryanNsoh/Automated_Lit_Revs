import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Sample data representing the number of papers associated with each subcategory
data = {
    "Category": [
        "Sensing and Data Acquisition",
        "Sensing and Data Acquisition",
        "Sensing and Data Acquisition",
        "Sensing and Data Acquisition",
        "Data Preprocessing and Quality Assurance",
        "Data Preprocessing and Quality Assurance",
        "Data Preprocessing and Quality Assurance",
        "Data Preprocessing and Quality Assurance",
        "Predictive Modeling for Irrigation Management",
        "Predictive Modeling for Irrigation Management",
        "Predictive Modeling for Irrigation Management",
        "Predictive Modeling for Irrigation Management",
        "Automated Irrigation Control Systems",
        "Automated Irrigation Control Systems",
        "Automated Irrigation Control Systems",
        "Automated Irrigation Control Systems",
        "System Architecture and Integration",
        "System Architecture and Integration",
        "System Architecture and Integration",
        "System Architecture and Integration",
        "Cybersecurity and Data Management",
        "Cybersecurity and Data Management",
        "Cybersecurity and Data Management",
        "Cybersecurity and Data Management",
        "System Reliability and Resilience",
        "System Reliability and Resilience",
        "System Reliability and Resilience",
        "System Reliability and Resilience",
    ],
    "Subcategory": [
        "Sensor Types",
        "Wireless Sensor Networks (WSN)",
        "Data Transmission Protocols",
        "Edge Computing",
        "Data Cleaning",
        "Data Transformation",
        "Data Fusion",
        "Data Quality Control",
        "Crop Water Requirement Prediction",
        "Irrigation Scheduling Optimization",
        "Soil Moisture Dynamics Modeling",
        "Yield Prediction and Optimization",
        "Closed-Loop Control",
        "Rule-Based Systems",
        "Open-Loop Control",
        "Human-in-the-Loop Control",
        "Interoperability",
        "Data Exchange Standards",
        "Integration with Legacy Systems",
        "Integration with Precision Agriculture",
        "Security Risks",
        "Security Measures",
        "Data Privacy",
        "Data Governance",
        "Fault Tolerance",
        "Anomaly Detection",
        "Predictive Maintenance",
        "Self-Healing Systems",
    ],
    "Papers": [
        10,
        5,
        8,
        4,
        7,
        6,
        3,
        5,
        9,
        8,
        5,
        6,
        4,
        7,
        5,
        3,
        6,
        4,
        7,
        8,
        5,
        6,
        4,
        3,
        8,
        5,
        7,
        6,
    ],
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Set the size of the plot
plt.figure(figsize=(14, 8))

# Create a color palette
palette = sns.color_palette("Paired", len(df["Subcategory"].unique()))

# Create the barplot with distinct color schemes for each main category
sns.barplot(
    x="Category", y="Papers", hue="Subcategory", data=df, dodge=True, palette=palette
)

# Rotate x labels for better readability
plt.xticks(rotation=45, ha="right")

# Set plot title and labels
plt.title(
    "Number of Papers Associated with Each Subcategory in Smart Irrigation Systems"
)
plt.xlabel("Category")
plt.ylabel("Number of Papers")

# Display the legend
plt.legend(title="Subcategory", bbox_to_anchor=(1.05, 1), loc="upper left")

# Show the plot
plt.tight_layout()
plt.show()
