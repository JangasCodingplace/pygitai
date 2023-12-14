import argparse
from . import cmd


def main():
    parser = argparse.ArgumentParser(
        description='A small package to optimize some git workflows'
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
        type=bool,
        default=False,
    )

    args = parser.parse_args()
    getattr(cmd, args.cmd)(**vars(args))
