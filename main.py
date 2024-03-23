from utils.research_paper_outline_generator import ResearchPaperOutlineGenerator
from utils.llm_api_handler import LLM_APIHandler
import asyncio

# Example usage
json_file = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline.json"
output_directory = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3"

# generator = ResearchPaperOutlineGenerator(json_file, output_directory)
# output_file = generator.generate_outline()
# print(f"YAML outline generated at: {output_file}")

api_key_path = r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"


# Sample usage for Gemini
async def gemini_example():
    handler = LLM_APIHandler(api_key_path)
    prompt = "What is the capital of France?"
    response = await handler.generate_gemini_content(prompt)
    print(response)

    # With JSON response format
    prompt = "What is the capital of France? return your response in json format. must be valid json"
    response_json = await handler.generate_gemini_content(
        prompt, response_format="json"
    )
    print(response_json)


# Sample usage for Haiku
async def haiku_example():
    handler = LLM_APIHandler(api_key_path)
    prompt = "Write a haiku about the beauty of nature."
    system_prompt = "You are a poet specializing in haikus. Create a beautiful and insightful haiku based on the given prompt."
    response = await handler.generate_claude_content(prompt, system_prompt)
    print(response)

    # With JSON response format
    system_prompt = "You are a poet specializing in haikus. Create a beautiful and insightful haiku based on the given prompt. return your response in json format. must be valid json"
    response_json = await handler.generate_claude_content(
        prompt, system_prompt, response_format="json"
    )
    print(response_json)


asyncio.run(gemini_example())
asyncio.run(haiku_example())
