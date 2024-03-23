from research_paper_outline_generator import ResearchPaperOutlineGenerator

# Test the class
json_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline.json"
output_directory = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3"
generator = ResearchPaperOutlineGenerator(json_file, output_directory)
output_file = generator.generate_outline()
print(f"YAML outline generated at: {output_file}")
