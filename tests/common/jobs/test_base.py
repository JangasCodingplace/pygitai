from argparse import Namespace

import pygitai.common.jobs.base as base


class TestJobBase:
    class TestJobA(base.JobBase):
        cli_configurable_name = "is_test"

        def exec_command(self, *args, **kwargs):
            return "foo"

    class TestJobB(base.JobBase):
        def exec_command(self, *args, **kwargs):
            return "bar"

    def test_perform_executed(self):
        cli_args = Namespace(
            is_test=True,
        )
        assert self.TestJobA().perform(cli_args=cli_args) == "foo"

    def test_perform_not_executed_by_false_cli_arg(self):
        cli_args = Namespace(
            is_test=False,
        )
        assert self.TestJobA().perform(cli_args=cli_args) is None

    def test_perform_not_executed_by_no_cli_arg(self):
        cli_args = Namespace()
        assert self.TestJobA().perform(cli_args=cli_args) is None

    def test_perform_always(self):
        cli_args = Namespace()
        assert self.TestJobB().perform(cli_args=cli_args) == "bar"
