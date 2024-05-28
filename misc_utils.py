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


def get_api_keys(source="local"):
    if source == "cloud":
        client = secretmanager.SecretManagerServiceClient()
        name = "projects/crop2cloud24/secrets/api-keys/versions/latest"
        response = client.access_secret_version(request={"name": name})
        api_keys = response.payload.data.decode("UTF-8")
        try:
            return json.loads(api_keys)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Google Cloud Secret Manager: {e}")
    else:
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
