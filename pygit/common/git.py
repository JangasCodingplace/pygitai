import subprocess
from dataclasses import dataclass

from .config import config
from .logger import get_logger

logger = get_logger(__name__, config.logger.level)


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
    def exec_commit(cls, title: str, body: str | None = None):
        """Execute the commit command"""
        cmd = ["git", "commit", "-m", f'"{title}"']
        if body:
            cmd.extend(["-m", f'"{body}"'])
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
        staged_files = Git.get_staged_files()

        return cls(
            staged_files=staged_files,
            diff={file_name: Git.get_diff(file_name) for file_name in staged_files},
        )

    def refresh(self):
        self.staged_files = Git.get_staged_files()
        self.diff = {
            file_name: Git.get_diff(file_name) for file_name in self.staged_files
        }


state = GitState.from_base_commands()
