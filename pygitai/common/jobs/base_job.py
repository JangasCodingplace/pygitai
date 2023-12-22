from abc import ABC, abstractmethod
from argparse import Namespace


class BaseJob(ABC):
    """Base class for Job.

    A Job will always be executed as part of a pipeline.

    Attributes:
        cli_configurable_name (str | None): The name of the
            attribute in the cli args that will be used to
            determine if this job should be executed. Only boolean
            values are supperted at the moment. If it is None, the
            job will always be executed.
        cli_args (Namespace): The cli arguments.
        kwargs (dict): The keyword arguments that were passed to the job.
    """

    cli_configurable_name: str | None = None

    def perform(self, cli_args: Namespace, *args, **kwargs):
        """Perform the job. This method is just a wrapper around
        `exec_command`. It's used to determine if the job should be
        executed or not.

        Args:
            cli_args (Namespace): The cli arguments. Those arguments
                will be bound to the job instance.
            **kwargs: The keyword arguments that were passed to the
                job. Those arguments will be bound to the job
                instance.
        """
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
        """Execute the command"""
        pass
