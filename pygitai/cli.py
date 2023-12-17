import argparse

from . import cmd
from .common.config import BASE_DIR
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


def main():
    pygit_setup()
    parser = argparse.ArgumentParser(
        description="A small package to optimize some git workflows"
    )

    subparsers = parser.add_subparsers(
        dest="cmd",
        help="Command to run",
    )

    parser_commit = subparsers.add_parser(
        "commit",
        help="Commit a directory",
    )
    parser_commit.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
    )
    parser_commit.add_argument(
        "--use-commit-body",
        action="store_true",
        default=False,
    )
    parser_commit.add_argument(
        "--include-ai-feedback",
        action="store_true",
        default=False,
    )
    parser_commit.add_argument(
        "--auto-stage-all",
        action="store_true",
        default=False,
    )

    parser_commit = subparsers.add_parser(
        "pr-review",
        help="Review for a pull request",
    )
    parser_commit.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
    )
    parser_commit.add_argument(
        "--target-branch",
        type=str,
    )

    args = parser.parse_args()
    getattr(cmd, args.cmd.replace("-", "_"))(**vars(args))
