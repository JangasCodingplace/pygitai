import sys

from . import llm
from .config import config
from .git import Git, PreCommitHook
from .git import state as git_state
from .logger import get_logger

# load custom project scope
sys.path.append((config.general.toplevel_directory / ".pygitai").as_posix())
import pygitai_customization  # noqa

try:
    LLM = getattr(llm, config.general.llm)
except AttributeError:
    LLM = getattr(pygitai_customization.llm, config.general.llm)


__all__ = [
    "config",
    "get_logger",
    "git_state",
    "Git",
    "PreCommitHook",
    "LLM",
]
