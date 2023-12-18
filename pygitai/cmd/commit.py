from argparse import Namespace

from pygitai.common import config, get_logger
from pygitai.common.jobs.api import (
    AutoStageAll,
    CommitTitle,
    FeedbackOnCommit,
    PreCommitHook,
)

logger = get_logger(__name__, config.logger.level)


def main(
    cli_args: Namespace,
    *args,
    **kwargs,
):
    """Commit command"""
    AutoStageAll().perform(cli_args=cli_args)
    PreCommitHook().perform(cli_args=cli_args)
    FeedbackOnCommit().perform(cli_args=cli_args)
    CommitTitle().perform(cli_args=cli_args)
