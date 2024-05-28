import os


def load_file(file_path):
    """Load the content of a file given its path."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def load_prompt_from_file(template_name):
    """Load the content of a template file given its name."""
    file_path = os.path.join("prompts", f"{template_name}.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Template file '{file_path}' does not exist.")
    return load_file(file_path)


def replace_dependencies(content, dependencies):
    """Replace placeholders in the content with the content of the corresponding files."""
    for key, filename in dependencies.items():
        placeholder = f"{{{key}}}"
        file_content = load_prompt_from_file(filename)
        content = content.replace(placeholder, file_content)
    return content


def get_prompt(template_name, dependencies=None, **kwargs):
    """Generate the final prompt by replacing placeholders in the template with file content and direct values."""
    if dependencies is None:
        dependencies = {}
    try:
        template_content = load_prompt_from_file(template_name)
        if dependencies:
            template_content = replace_dependencies(template_content, dependencies)
        final_content = template_content.format(**kwargs)
        return final_content
    except KeyError as e:
        missing_key = str(e).strip("'")
        raise ValueError(
            f"Missing argument for template '{template_name}': {missing_key}"
        )
    except FileNotFoundError as e:
        raise ValueError(str(e))
