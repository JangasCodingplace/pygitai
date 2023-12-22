import argparse

from . import cmd
from .cmd.setup import pygit_setup


def main():
    parser = argparse.ArgumentParser(
        description="A small package to optimize some git workflows"
    )

    subparsers = parser.add_subparsers(
        dest="cmd",
        help=(
            "Command to run. Choices: "
            "[commit, pr-review, setup-branch, setup, customization, ui]"
        ),
    )

    parser_commit = subparsers.add_parser(
        "commit",
        help="Commit all staged changes. This is a LLM command.",
    )
    parser_commit.add_argument(
        "--use-commit-body",
        action="store_true",
        default=False,
        help="Add an extended body to the commit message",
    )
    parser_commit.add_argument(
        "--include-ai-feedback",
        action="store_true",
        default=False,
        help="Include AI feedback before commiting code",
    )
    parser_commit.add_argument(
        "--auto-stage-all",
        action="store_true",
        default=False,
        help="Automatically stage all unstaged files",
    )

    parser_pr_review = subparsers.add_parser(
        "pr-review",
        help="Get AI Review for different branches / hashes",
    )
    parser_pr_review.add_argument(
        "--target-branch",
        type=str,
        help="Target branch to compare against",
    )

    subparsers.add_parser(
        "setup-branch",
        help="Setup a branch and enrich branch info for better ai help",
    )

    customization = subparsers.add_parser(
        "customization",
        help="Customize pygitai",
    )

    customization_subparsers = customization.add_subparsers(
        dest="customization_cmd",
        help="Customization command to run. Choices: [job, llm, template]",
    )

    customization_job = customization_subparsers.add_parser(
        "job",
        help="Customize pygitai job",
    )
    customization_job.add_argument(
        "--name",
        type=str,
        help="Name of custom Job Class to create",
    )
    customization_job.add_argument(
        "--type",
        type=str,
        help="Type of job to create. Available types: [base, llm]",
    )

    customization_llm = customization_subparsers.add_parser(
        "llm",
        help="Customize pygitai llm",
    )
    customization_llm.add_argument(
        "--name",
        type=str,
        help="Name of custom LLM Class to create",
    )

    customization_template = customization_subparsers.add_parser(
        "template",
        help="Overwrite default pygitai templates",
    )
    customization_template.add_argument(
        "--llm-job-name",
        type=str,
        help="Name of LLM Job Class to overwrite template for",
    )
    customization_template.add_argument(
        "--template-group",
        type=str,
        required=False,
        default="",
        help=(
            "Group of template to overwrite. "
            "If not provided, all templates for the given LLM Job will be overwritten."
            "Available groups: [system, user, revision]"
        ),
    )

    subparsers.add_parser(
        "setup",
        help=(
            "Setup pygitai. This command is currently optional. "
            "The setup is done automatically when you run any other command."
        ),
    )

    args = parser.parse_args()

    pygit_setup()
    getattr(cmd, args.cmd.replace("-", "_"))(cli_args=args, **vars(args))
