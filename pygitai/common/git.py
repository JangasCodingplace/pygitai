import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import config
from .logger import get_logger

logger = get_logger(__name__, config.logger.level)


def get_ignored_file_patterns() -> list[str]:
    """Get the patterns of the files to ignore.

    The patterns are read from the `.pygitaiignore` file in the top
    level directory of the git repo.


    Returns:
    --------
    List of patterns to ignore.
    """
    top_level_directory = Git.get_toplevel_directory()
    pygitai_ignore_file = top_level_directory / ".pygitaiignore"
    if pygitai_ignore_file.exists():
        with pygitai_ignore_file.open("r") as f:
            return f.read().splitlines()
    return []


def file_name_matches_patterns(file_name: str, patterns: list[str]) -> bool:
    """Check if the file name matches any of the patterns.


    Attributes:
    -----------
    file_name:
        File name to check
    patterns:
        List of patterns to check against the file name


    Returns:
    --------
    True if the file name matches any of the patterns, False otherwise.


    Examples:
    ---------
    >>> file_name_matches_patterns("poetry.lock", ["poetry.lock"])
    True
    >>> file_name_matches_patterns("poetry.lock", ["*.lock"])
    True
    >>> file_name_matches_patterns("poetry.lock", ["*.toml"])
    False
    """
    for pattern in patterns:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    return False


class PreCommitHook:
    @classmethod
    def run(cls, file_names: list[str], allow_retry: bool = True, *args, **kwargs):
        cmd = ["pre-commit", "run", "--files"] + file_names
        logger.info(f'cmd {" ".join(cmd)}')
        pre_commit_response = subprocess.run(cmd)
        try:
            pre_commit_response.check_returncode()
        except subprocess.CalledProcessError:
            if allow_retry:
                Git.exec_stage_files(file_names)
                cls.run(file_names, allow_retry=False)
            else:
                raise


class Git:
    @classmethod
    def get_staged_files(cls) -> list[str]:
        """Get all staged files"""
        cmd = ["git", "diff", "--name-only", "--cached"]
        logger.info(f'cmd {" ".join(cmd)}')
        diff = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
        )
        logger.info(diff.stdout)
        return diff.stdout.split("\n")

    @classmethod
    def get_diff(cls, file_name: str | None = None):
        """Get the diff of all staged git files"""
        cmd = ["git", "diff", "--cached"]
        if file_name:
            cmd.append(file_name)

        logger.info(f'cmd {" ".join(cmd)}')

        diff = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
        )
        return diff.stdout

    @classmethod
    def get_diff_between_branches(
        cls, branch_1: str, branch_2: str, number_of_context_lines: int = 10
    ):
        """Get the diff between two branches"""
        cmd = ["git", "diff", branch_1, branch_2]
        if number_of_context_lines:
            cmd.extend([f"-U{number_of_context_lines}"])

        # exclude files from .pygitaiignore
        excludes = [f":(exclude){pattern}" for pattern in get_ignored_file_patterns()]

        cmd.extend(["--", "."])
        cmd.extend(excludes)

        logger.info(f'cmd {" ".join(cmd)}')
        diff = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
        )
        return diff.stdout

    @classmethod
    def get_current_branch(cls) -> str:
        """Get the current branch"""
        cmd = ["git", "branch", "--show-current"]
        logger.info(f'cmd {" ".join(cmd)}')
        branch = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
        )
        return branch.stdout.strip()

    @classmethod
    def get_toplevel_directory(cls) -> Path:
        """Get the top level directory of the git repo"""
        cmd = ["git", "rev-parse", "--show-toplevel"]
        logger.info(f'cmd {" ".join(cmd)}')
        toplevel_directory = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
        )
        return Path(toplevel_directory.stdout.strip())

    @classmethod
    def exec_commit(cls, title: str, body: str | None = None):
        """Execute the commit command"""
        cmd = ["git", "commit", "-m", f"{title}"]
        if body:
            cmd.extend(["-m", f"{body}"])
        logger.info(f'cmd {" ".join(cmd)}')
        subprocess.run(cmd)
        state.refresh()

    @classmethod
    def exec_stage_files(cls, file_names: list[str]):
        """Stage files"""
        cmd = ["git", "add"] + file_names
        logger.info(f'cmd {" ".join(cmd)}')
        subprocess.run(cmd)
        state.refresh()


@dataclass
class GitState:
    staged_files: list[str]
    diff: dict[str, str]

    @classmethod
    def from_base_commands(cls) -> "GitState":
        ignored_file_patterns = get_ignored_file_patterns()
        staged_files = [
            fp
            for fp in Git.get_staged_files()
            if fp and not file_name_matches_patterns(fp, ignored_file_patterns)
        ]

        return cls(
            staged_files=staged_files,
            diff={file_name: Git.get_diff(file_name) for file_name in staged_files},
        )

    def refresh(self):
        ignored_file_patterns = get_ignored_file_patterns()
        self.staged_files = [
            fp
            for fp in Git.get_staged_files()
            if fp and not file_name_matches_patterns(fp, ignored_file_patterns)
        ]
        self.diff = {
            file_name: Git.get_diff(file_name) for file_name in self.staged_files
        }


state = GitState.from_base_commands()
