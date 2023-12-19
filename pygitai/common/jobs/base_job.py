from abc import ABC, abstractmethod
from argparse import Namespace


class BaseJob(ABC):
    """Base class for Job"""

    cli_configurable_name: str | None = None

    def perform(self, cli_args: Namespace, *args, **kwargs):
        self.cli_args = cli_args
        self.kwargs = kwargs

        if self.cli_configurable_name and self.cli_configurable_name not in cli_args:
            return
        elif self.cli_configurable_name and not getattr(
            cli_args, self.cli_configurable_name
        ):
            # getattr will raise an Error if the attribute is not found
            # that's why there are seperate if statements
            return
        else:
            return self.exec_command(*args, **kwargs)

    @abstractmethod
    def exec_command(self, *args, **kwargs):
        pass
