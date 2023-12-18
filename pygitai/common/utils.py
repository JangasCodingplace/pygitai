import re


def camel_to_snake(name):
    """Convert camel case to snake case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
