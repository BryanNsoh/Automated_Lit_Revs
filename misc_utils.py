# misc_utils.py
import os
import json
from google.cloud import secretmanager


async def prepare_text_for_json(text):
    # Replace backslashes with double backslashes
    text = text.replace("\\", "\\\\")

    # Replace double quotes with escaped double quotes
    text = text.replace('"', '\\"')

    # Replace newline characters with escaped newline characters
    text = text.replace("\n", "\\n")

    # Replace tab characters with escaped tab characters
    text = text.replace("\t", "\\t")

    # Replace form feed characters with escaped form feed characters
    text = text.replace("\f", "\\f")

    # Replace backspace characters with escaped backspace characters
    text = text.replace("\b", "\\b")

    # Replace carriage return characters with escaped carriage return characters
    text = text.replace("\r", "\\r")

    # Wrap the escaped text in double quotes to make it a valid JSON string
    json_string = f'"{text}"'

    return json_string


import os
import json


def get_api_keys(source="env"):
    if source == "local":
        with open(
            os.path.expanduser(
                r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\keys\api_keys.json"
            ),
            "r",
        ) as file:
            api_keys = file.read()
            try:
                return json.loads(api_keys)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in local file: {e}")
    else:
        return {
            "CLAUDE_API_KEY": os.getenv("CLAUDE_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "COHERE_API_KEY": os.getenv("COHERE_API_KEY"),
            "TOGETHER_API_KEY": os.getenv("TOGETHER_API_KEY"),
            "SCOPUS_API_KEY": os.getenv("SCOPUS_API_KEY"),
            "CORE_API_KEY": os.getenv("CORE_API_KEY"),
        }
