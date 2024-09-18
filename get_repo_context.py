import os
import datetime
from pathlib import Path
import pyperclip
import requests
import xml.etree.ElementTree as ET

# Exclude lists
FOLDER_EXCLUDE = {".git", "__pycache__", "node_modules", ".venv", "archive", "deployment_scripts"}
FILE_EXTENSION_EXCLUDE = {".exe", ".dll", ".so", ".pyc"}

# Define customizable tags with optional Google Docs URLs (the content of the tag will be fetched from the URL)
CUSTOM_TAGS = [
    {
        "name": "instructions",
        "url": None
    },
    {
        "name": "docs",
        "url": None  # No URL provided, will use a placeholder
    }
    # Add more tags as needed
    # {
    #     "name": "notes",
    #     "url": "https://docs.google.com/document/d/1emAdwa-92zF8Jjx53qkMJX526rzIJ5ZSlxy0H2nrrzg/export?format=txt"
    # },
]

def obfuscate_env_value(value):
    return "********"

def create_file_element(file_path, root_folder):
    relative_path = os.path.relpath(file_path, root_folder)
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1]

    file_elem = ET.Element("file")
    
    name_elem = ET.SubElement(file_elem, "name")
    name_elem.text = file_name

    path_elem = ET.SubElement(file_elem, "path")
    path_elem.text = relative_path

    if file_extension not in FILE_EXTENSION_EXCLUDE:
        content_elem = ET.SubElement(file_elem, "content")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                if file_name == ".env":
                    lines = content.split("\n")
                    obfuscated_lines = []
                    for line in lines:
                        if "=" in line:
                            key, _ = line.split("=", 1)
                            obfuscated_lines.append(f"{key.strip()}={obfuscate_env_value('')}")
                        else:
                            obfuscated_lines.append(line)
                    content = "\n".join(obfuscated_lines)
                content_elem.text = content
        except UnicodeDecodeError:
            content_elem.text = "Binary or non-UTF-8 content not displayed"
    else:
        content_elem = ET.SubElement(file_elem, "content")
        content_elem.text = "File excluded based on extension"

    return file_elem

def get_repo_structure(root_folder):
    repo_struct = ET.Element("repository_structure")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp_elem = ET.SubElement(repo_struct, "timestamp")
    timestamp_elem.text = timestamp

    for root, dirs, files in os.walk(root_folder):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in FOLDER_EXCLUDE]
        
        rel_path = os.path.relpath(root, root_folder)
        dir_name = os.path.basename(root) if rel_path != "." else os.path.basename(root_folder)
        directory_elem = ET.SubElement(repo_struct, "directory", name=dir_name)
        
        for file in files:
            file_path = os.path.join(root, file)
            file_elem = create_file_element(file_path, root_folder)
            directory_elem.append(file_elem)

    return repo_struct

def copy_to_clipboard(text):
    pyperclip.copy(text)

def fetch_content_from_google_doc(export_url):
    """
    Fetches the content of a public Google Doc in plain text format.

    Args:
        export_url (str): The export URL of the Google Doc.

    Returns:
        str: The content of the Google Doc.

    Raises:
        Exception: If the document cannot be fetched.
    """
    try:
        response = requests.get(export_url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to fetch content. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching content from {export_url}: {e}")
        return f"<!-- Failed to fetch content for this section: {e} -->"

def main():
    """
    Extracts the repository context and copies it to the clipboard.

    This function performs the following tasks:
    1. Determines the root folder of the repository.
    2. Generates a timestamp for the context.
    3. Extracts the repository structure.
    4. Constructs the XML structure with custom tags, fetching content from Google Docs if URLs are provided.
    5. Copies the entire XML to the clipboard.
    """
    root_folder = os.getcwd()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize XML root
    context_elem = ET.Element("context")
    
    # Add timestamp
    timestamp_elem = ET.SubElement(context_elem, "timestamp")
    timestamp_elem.text = timestamp

    # Add custom tags with content fetched from Google Docs or placeholders
    for tag in CUSTOM_TAGS:
        tag_name = tag.get("name")
        tag_url = tag.get("url")
        tag_elem = ET.SubElement(context_elem, tag_name)
        if tag_url:
            content = fetch_content_from_google_doc(tag_url)
            tag_elem.text = content
        else:
            tag_elem.text = f"<!-- Add your {tag_name} here -->"

    # Add repository structure
    repo_structure = get_repo_structure(root_folder)
    context_elem.append(repo_structure)

    # Add additional information concisely
    additional_info = (
        f"This context includes the repository structure excluding directories: {', '.join(FOLDER_EXCLUDE)} "
        f"and file extensions: {', '.join(FILE_EXTENSION_EXCLUDE)}. Sensitive information in .env files has been obfuscated."
    )
    additional_info_elem = ET.SubElement(context_elem, "additional_information")
    additional_info_elem.text = additional_info

    # Generate XML string
    xml_str = ET.tostring(context_elem, encoding='utf-8').decode('utf-8')

    # Pretty-print the XML
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_as_string = dom.toprettyxml(indent="    ")

    # Copy to clipboard
    copy_to_clipboard(pretty_xml_as_string)

    print("Repository context has been copied to the clipboard.")

if __name__ == "__main__":
    main()
