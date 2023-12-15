import json
import subprocess

from pygit.common import OpenAI, ResponseParserBase, config, get_logger

logger = get_logger(__name__, config.logger.level)


class CommitMessageLLMParser(ResponseParserBase):
    @staticmethod
    def parse(response, prompt):
        return response.json()["choices"][0]["message"]["content"]


class CommitMessageLLM(OpenAI):
    llm_response_parser = CommitMessageLLMParser
    config = config.openai


def run_pre_commit_for_file(file_names: list[str], use_poetry: bool = True):
    """Run pre commit for a single file"""
    cmd = []
    if use_poetry:
        cmd.extend(["poetry", "run"])
    cmd.extend(["pre-commit", "run", "--files"])
    cmd.extend(file_names)
    logger.info(f'cmd {" ".join(cmd)}')
    pre_commit_response = subprocess.run(cmd)
    pre_commit_response.check_returncode()


def get_staged_files() -> list[str]:
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


def get_diff(file_name: str | None = None):
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


def exit_commit(title: str, body: str | None = None):
    """Exit the commit command"""
    cmd = ["git", "commit", "-m", f'"{title}"']
    if body:
        cmd.extend(["-m", f'"{body}"'])
    logger.info(f'cmd {" ".join(cmd)}')
    subprocess.run(cmd)


def get_llm_commit_title_response(diffs: dict[str, str]):
    """Get the response from the LLM"""
    return CommitMessageLLM.exec_prompt(
        prompt=[
            {
                "role": "system",
                "content": (
                    "You are an assistant for writing a title for a commit "
                    "message. The user will send following information to you: \n"
                    "1. The diff of all staged git cached files. \n"
                    "2. Optional: The description of the current task the user is"
                    "working at\n"
                    "3. Optional: Messages of previous commits\n"
                    "Please response with only a very short description for the "
                    "commit message title."
                ),
            },
            {
                "role": "user",
                "content": (f"My diff: {json.dumps(diffs)}"),
            },
        ]
    )


def get_llm_commit_msg_body_response(diffs: dict[str, str]):
    """Get the response from the LLM"""
    return CommitMessageLLM.exec_prompt(
        prompt=[
            {
                "role": "system",
                "content": (
                    "You are an assistant for writing a body for a commit."
                    "The user will send following information to you: \n"
                    "1. The diff of all staged files. \n"
                    "2. Optional: The description of the current task the user is"
                    "working at\n"
                    "3. Optional: Messages of previous commits\n"
                    "Please response with a brief description for the commit which can "
                    "be used for better understanding of the commit."
                    "It's allowed to use multiple sentences or an enumeration."
                ),
            },
            {
                "role": "user",
                "content": (f"My diff: {json.dumps(diffs)}"),
            },
        ]
    )


def main(*args, **kwargs):
    """Commit command"""
    staged_files = get_staged_files()

    if config.git.pre_commit:
        run_pre_commit_for_file(staged_files)

    diffs = {file_name: get_diff(file_name) for file_name in staged_files if file_name}

    commit_title = get_llm_commit_title_response(diffs)
    commit_body = get_llm_commit_msg_body_response(diffs)
    exit_commit(commit_title, commit_body)
