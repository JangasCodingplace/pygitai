import fnmatch

from .config import BASE_DIR


def get_ignored_file_patterns() -> list[str]:
    root_dir = BASE_DIR.parent
    pygitai_ignore_file = root_dir / ".pygitaiignore"
    if pygitai_ignore_file.exists():
        with pygitai_ignore_file.open("r") as f:
            return f.read().splitlines()
    return []


def file_name_matches_patterns(file_name: str, patterns: list[str]) -> bool:
    """Check if the file name matches any of the patterns"""
    for pattern in patterns:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    return False
