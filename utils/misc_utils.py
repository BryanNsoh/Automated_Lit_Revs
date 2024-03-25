import json
import asyncio


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
