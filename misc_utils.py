# misc_utils.py
import os
import json
from google.cloud import secretmanager
from dotenv import load_dotenv  # New import


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


import os
import logging


def get_api_keys(source="env"):
    if source == "local":
        load_dotenv()  # Load environment variables from .env file
    
    # Remove or comment out these lines:
    # logging.info(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
    # logging.info(f"CORE_API_KEY: {os.getenv('CORE_API_KEY')}")

    # Instead, log that the keys were loaded successfully without revealing them:
    logging.info("API keys loaded successfully")

    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "CORE_API_KEY": os.getenv("CORE_API_KEY"),
    }
