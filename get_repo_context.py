import os
import datetime
from pathlib import Path

GLOBAL_EXCLUDE = {".git", "__pycache__", "node_modules", ".venv"}

def create_file_element(file_path, root_folder):
    relative_path = os.path.relpath(file_path, root_folder)
    file_name = os.path.basename(file_path)

    file_element = [
        f"    <file>\n        <name>{file_name}</name>\n        <path>{relative_path}</path>\n"
    ]

    file_element.append("        <content>\n")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_element.append(file.read())
    except UnicodeDecodeError:
        file_element.append("Binary or non-UTF-8 content not displayed")
    file_element.append("\n        </content>\n")

    file_element.append("    </file>\n")
    return "".join(file_element)

def get_repo_structure(root_folder):
    structure = ["<repository_structure>\n"]
    root_path = Path(root_folder)

    for root, dirs, files in os.walk(root_folder):
        rel_path = os.path.relpath(root, root_folder)
        
        # Exclude directories at the current level
        dirs[:] = [d for d in dirs if d not in GLOBAL_EXCLUDE]
        
        level = rel_path.count(os.sep)
        indent = "    " * level

        structure.append(f'{indent}<directory name="{os.path.basename(root)}">\n')
        for file in files:
            file_path = os.path.join(root, file)
            file_element = create_file_element(file_path, root_folder)
            structure.append(indent + file_element)
        structure.append(f"{indent}</directory>\n")

    structure.append("</repository_structure>\n")
    return "".join(structure)

def main():
    root_folder = os.getcwd()
    base_dir = os.path.basename(root_folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(root_folder, f"{base_dir}_context_{timestamp}.txt")

    for file in os.listdir(root_folder):
        if file.startswith(f"{base_dir}_context_") and file.endswith(".txt"):
            os.remove(os.path.join(root_folder, file))
            print(f"Deleted previous context file: {file}")

    repo_structure = get_repo_structure(root_folder)

    with open(output_file, "w", encoding="utf-8") as f:
        # Write global variables with docstrings
        for name, value in globals().items():
            if name.isupper() and isinstance(value, str) and value.strip():
                f.write(f"{name} = '''\n{value.strip()}\n'''\n\n")
        f.write(f"\nContext extraction timestamp: {timestamp}\n\n")
        f.write(repo_structure)

    print(f"Fresh repository context has been extracted to {output_file}")

if __name__ == "__main__":
    main()
