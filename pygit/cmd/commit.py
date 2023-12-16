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


def exec_commit(title: str, body: str | None = None):
    """Execute the commit command"""
    cmd = ["git", "commit", "-m", f'"{title}"']
    if body:
        cmd.extend(["-m", f'"{body}"'])
    logger.info(f'cmd {" ".join(cmd)}')
    subprocess.run(cmd)


def get_llm_commit_title_response(diffs: dict[str, str], prompt_override: list = None):
    """Get the response from the LLM"""
    prompt = prompt_override or [
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
    return CommitMessageLLM.exec_prompt(prompt=prompt)


def get_llm_commit_msg_body_response(
    diffs: dict[str, str], prompt_override: list = None
):
    """Get the response from the LLM"""
    prompt = prompt_override or [
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
    return CommitMessageLLM.exec_prompt(prompt=prompt)


def get_llm_feedback_response(diffs: dict[str, str], prompt_override: list = None):
    """Get the response from the LLM"""
    prompt = prompt_override or [
        {
            "role": "system",
            "content": (
                "You are a Code reviewer for a commit."
                "The user will send following information to you: \n"
                "1. The diff of a single staged file or all staged files. \n"
                "2. Optional: The description of the current task the user is"
                "working at\n"
                "3. Optional: Code Guidelines\n"
                "Your Job is to review the code and give feedback to the user."
            ),
        },
        {
            "role": "user",
            "content": (f"My diff: {json.dumps(diffs)}"),
        },
    ]
    return CommitMessageLLM.exec_prompt(prompt=prompt)


def ask_for_user_feedback(prompt_output_context: str, prompt_output: str):
    """Ask the user for feedback"""
    logger.info(f"Prompt Output for {prompt_output_context}: {prompt_output}")
    agree = input("Do you agree with the prompt output? [y/n]")
    if agree.lower() == "y":
        return "y"
    elif agree.lower() == "n":
        recommendation = input("Any recommendation for a better output?")
        return recommendation
    else:
        logger.warn("Wrong input. Please only enter 'y' or 'n'")
        return ask_for_user_feedback(prompt_output_context, prompt_output)


def process_user_feedback_loop_commit_tile(diffs: dict[str, str]) -> str:
    prompt_override = None
    user_feedback = None
    while user_feedback != "y":
        commit_title, commit_title_full_context = get_llm_commit_title_response(
            diffs, prompt_override=prompt_override
        )
        user_feedback = ask_for_user_feedback(
            prompt_output_context="commit_title",
            prompt_output=commit_title,
        )
        if user_feedback != "y":
            prompt_override = commit_title_full_context + [
                {
                    "role": "user",
                    "content": f"""
                        I don't agree with your feedback.
                        Here is my Feedback:
                        {user_feedback or 'No Feedback provided'}
                    """,
                },
            ]
    return commit_title


def process_user_feedback_loop_commit_body(diffs: dict[str, str]) -> str:
    user_feedback = None
    prompt_override = None
    while user_feedback != "y":
        commit_body, commit_body_full_context = get_llm_feedback_response(
            diffs, prompt_override=prompt_override
        )
        user_feedback = ask_for_user_feedback(
            prompt_output_context="ai_code_feedback",
            prompt_output=commit_body,
        )
        if user_feedback != "y":
            prompt_override = commit_body_full_context + [
                {
                    "role": "user",
                    "content": f"""
                        I don't agree with the commit message.
                        Here is my Feedback:
                        {user_feedback or 'No Feedback provided'}

                        Please try again.
                    """,
                },
            ]
    return commit_body


def main(
    use_commit_body: bool = False,
    include_ai_feedback: bool = False,
    *args,
    **kwargs,
):
    """Commit command"""
    staged_files = get_staged_files()

    if config.git.pre_commit:
        run_pre_commit_for_file(staged_files)

    diffs = {file_name: get_diff(file_name) for file_name in staged_files if file_name}

    if include_ai_feedback:
        process_user_feedback_loop_commit_body(diffs)

    commit_title = process_user_feedback_loop_commit_tile(diffs)
    if use_commit_body:
        commit_body = process_user_feedback_loop_commit_body(diffs)
    else:
        commit_body = None
        logger.info("No extended commit body provided")

    exec_commit(commit_title, commit_body)
