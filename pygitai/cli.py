import argparse
import shutil

from . import cmd
from .common.config import BASE_DIR, config
from .common.db_api import BranchInfoDBAPI
from .common.git import Git


def pygit_setup():
    toplevel_directory = Git.get_toplevel_directory()
    pygitai_project_config_dir = toplevel_directory / ".pygitai"
    pygitai_project_config_dir.mkdir(exist_ok=True)
    # add .gitignore to pygitai directory if it doesn't exist
    pygitai_gitignore_file = pygitai_project_config_dir / ".gitignore"
    if not pygitai_gitignore_file.exists():
        pygitignore_default_file = BASE_DIR / "assets" / ".gitignore"
        pygitignore_default_file_contents = pygitignore_default_file.read_text()
        pygitai_gitignore_file.write_text(pygitignore_default_file_contents)

    # create config.ini if it doesn't exist
    pygitai_config_file = pygitai_project_config_dir / "config.ini"
    if not pygitai_config_file.exists():
        pygitai_default_config_file = BASE_DIR / "assets" / "config.ini"
        pygitai_default_config_file_contents = pygitai_default_config_file.read_text()
        pygitai_config_file.write_text(pygitai_default_config_file_contents)

    # create pygitai_customizations directory if it doesn't exist by copying from assets
    pygitai_customizations_dir = pygitai_project_config_dir / "pygitai_customization"
    if not pygitai_customizations_dir.exists():
        pygitai_customizations_assets_dir = (
            BASE_DIR / "assets" / "pygitai_customization"
        )
        shutil.copytree(pygitai_customizations_assets_dir, pygitai_customizations_dir)

    if not config.general.db_name.exists():
        BranchInfoDBAPI.create_table_if_not_exists()


def main():
    pygit_setup()
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

    args = parser.parse_args()
    getattr(cmd, args.cmd.replace("-", "_"))(cli_args=args, **vars(args))
