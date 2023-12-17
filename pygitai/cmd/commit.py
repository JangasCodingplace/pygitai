import json
from pathlib import Path

import jinja2

from pygitai.common import (
    Git,
    OpenAI,
    PreCommitHook,
    ResponseParserBase,
    config,
    get_logger,
    git_state,
)
from pygitai.common.db_api import BranchInfoDBAPI

logger = get_logger(__name__, config.logger.level)

PROMPT_PATH = config.general.template_dir / "prompts" / "openai"


def get_prompt_from_template(
    template_dir_path: Path,
    file_name: str,
    context: dict,
) -> str:
    """Get the prompt from the template"""
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir_path))
    template = template_env.get_template(file_name)
    return template.render(**context)


def get_llm_initial_message(
    template_dir_path: Path,
    base_file_name: str,
    context_system: dict | None = None,
    context_user: dict | None = None,
):
    """Get the initial message from the LLM"""
    content_system = get_prompt_from_template(
        template_dir_path=template_dir_path,
        file_name=f"{base_file_name}_system.txt",
        context=context_system or {},
    )
    content_user = get_prompt_from_template(
        template_dir_path=PROMPT_PATH,
        file_name=f"{base_file_name}_user.txt",
        context=context_user or {},
    )
    prompt = [
        {
            "role": "system",
            "content": content_system,
        },
        {
            "role": "user",
            "content": content_user,
        },
    ]
    return prompt


class CommitMessageLLMParser(ResponseParserBase):
    @staticmethod
    def parse(response, prompt):
        return response.json()["choices"][0]["message"]["content"]


class CommitMessageLLM(OpenAI):
    llm_response_parser = CommitMessageLLMParser
    config = config.openai


def get_llm_commit_title_response(diffs: dict[str, str], prompt_override: list = None):
    """Get the response from the LLM"""
    base_file = "commit_title"
    prompt = prompt_override or get_llm_initial_message(
        template_dir_path=PROMPT_PATH,
        base_file_name=base_file,
        context_user={"diff": json.dumps(diffs)},
    )
    return CommitMessageLLM.exec_prompt(prompt=prompt)


def get_llm_response(
    base_file_name: str,
    context_system: dict | None = None,
    context_user: dict | None = None,
    prompt_override: list = None,
):
    """Get the response from the LLM"""
    prompt = prompt_override or get_llm_initial_message(
        template_dir_path=PROMPT_PATH,
        base_file_name=base_file_name,
        context_system=context_system or {},
        context_user=context_user or {},
    )
    return CommitMessageLLM.exec_prompt(prompt=prompt)


def get_llm_commit_msg_body_response(
    diffs: dict[str, str], prompt_override: list = None
):
    """Get the response from the LLM"""
    base_file = "commit_body"
    prompt = prompt_override or get_llm_initial_message(
        template_dir_path=PROMPT_PATH,
        base_file_name=base_file,
        context_user={"diff": json.dumps(diffs)},
    )
    return CommitMessageLLM.exec_prompt(prompt=prompt)


def get_llm_feedback_response(diffs: dict[str, str], prompt_override: list = None):
    """Get the response from the LLM"""
    base_file = "feedback_on_commit"
    prompt = prompt_override or get_llm_initial_message(
        template_dir_path=PROMPT_PATH,
        base_file_name=base_file,
        context_user={"diff": json.dumps(diffs)},
    )
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


def process_user_feedback_llm_loop(
    context: str,
    context_user: dict | None = None,
    context_system: dict | None = None,
) -> str:
    prompt_override = None
    user_feedback = None
    while user_feedback != "y":
        prompt_output, prompt_output_full_context = get_llm_response(
            base_file_name=context,
            prompt_override=prompt_override,
            context_user=context_user or {},
            context_system=context_system or {},
        )
        user_feedback = ask_for_user_feedback(
            prompt_output_context=context,
            prompt_output=prompt_output,
        )
        if user_feedback != "y":
            revision_prompt = get_prompt_from_template(
                template_dir_path=PROMPT_PATH,
                file_name=f"{context}_revision.txt",
                context={"feedback": user_feedback or "No further info provided"},
            )
            prompt_override = prompt_output_full_context + [
                {
                    "role": "user",
                    "content": revision_prompt,
                },
            ]
    return prompt_output


def main(
    use_commit_body: bool = False,
    include_ai_feedback: bool = False,
    auto_stage_all: bool = False,
    *args,
    **kwargs,
):
    """Commit command"""
    if auto_stage_all:
        Git.exec_stage_files(["-A"])

    if config.git.pre_commit:
        PreCommitHook.run(git_state.staged_files)

    branch_info = BranchInfoDBAPI.get(Git.get_current_branch())

    if include_ai_feedback:
        process_user_feedback_llm_loop(
            context="feedback_on_commit",
            context_user={
                "diff": json.dumps(git_state.diff),
                "purpose": branch_info.purpose or "No purpose provided",
            },
        )

    commit_title = process_user_feedback_llm_loop(
        context="commit_title",
        context_user={
            "diff": json.dumps(git_state.diff),
            "purpose": branch_info.purpose or "No purpose provided",
        },
    )
    if use_commit_body:
        commit_body = process_user_feedback_llm_loop(
            context="commit_body",
            context_user={
                "diff": json.dumps(git_state.diff),
                "purpose": branch_info.purpose or "No purpose provided",
            },
        )
    else:
        commit_body = None
        logger.info("No extended commit body provided")

    Git.exec_commit(commit_title, commit_body)
