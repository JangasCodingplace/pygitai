import re
from pathlib import Path

import jinja2


def camel_to_snake(name):
    """Convert camel case to snake case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def load_template_file(
    template_path: Path,
    context: dict,
) -> str:
    """Get the prompt from the template"""
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent)
    )
    file_name = template_path.name
    template = template_env.get_template(file_name)
    return template.render(**context)
