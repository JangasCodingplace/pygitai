import re
from pathlib import Path

import jinja2


def camel_to_snake(name: str) -> str:
    """Convert camel case to snake case.


    Attributes:
    -----------
    name:
        Name to convert from camel case to snake case.


    Returns:
    --------
    Name in snake case.


    Examples:
    ---------
    >>> camel_to_snake("snake_case")
    'snake_case'
    >>> camel_to_snake("CamelCase")
    'camel_case'
    >>> camel_to_snake("ABCOther")
    'abc_other'
    """
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def load_template_file(
    template_path: Path,
    context: dict,
) -> str:
    """Load a template file and render it with the given context.


    Attributes:
    -----------
    template_path:
        Full path to the template file.
    context:
        Dictionary with the context to render the template.


    Returns:
    --------
    Rendered template as a string.
    """
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent)
    )
    file_name = template_path.name
    template = template_env.get_template(file_name)
    return template.render(**context)
