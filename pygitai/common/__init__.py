import sys

from . import llm
from .config import config
from .git import Git, PreCommitHook
from .git import state as git_state
from .logger import get_logger

customization_defined = False
try:
    # load custom project scope
    sys.path.append((config.general.toplevel_directory / ".pygitai").as_posix())
    import pygitai_customization  # noqa

    customization_defined = True
except ModuleNotFoundError:
    pass

try:
    LLM = getattr(llm, config.general.llm)
except AttributeError:
    if customization_defined:
        LLM = getattr(pygitai_customization.llm, config.general.llm)
    else:
        raise


__all__ = [
    "config",
    "get_logger",
    "git_state",
    "Git",
    "PreCommitHook",
    "LLM",
]
