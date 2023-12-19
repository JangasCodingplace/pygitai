from argparse import Namespace

from pygitai.common.jobs.api import CodeReview


def main(
    cli_args: Namespace,
    *args,
    **kwargs,
):
    CodeReview().perform(cli_args)
