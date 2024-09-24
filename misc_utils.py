import os
import logging
from dotenv import load_dotenv

def get_api_keys(source="env"):
    if source == "local":
        load_dotenv(override=True)  # Load environment variables from .env file
    
    # Remove or comment out these lines:
    # logging.info(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
    # logging.info(f"CORE_API_KEY: {os.getenv('CORE_API_KEY')}")

    # Instead, log that the keys were loaded successfully without revealing them:
    logging.info("API keys loaded successfully")

    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "CORE_API_KEY": os.getenv("CORE_API_KEY"),
    }
