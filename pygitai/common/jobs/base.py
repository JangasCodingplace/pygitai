from abc import ABC, abstractmethod
from argparse import Namespace
from pathlib import Path
from typing import Generic, Type, TypeVar

from pygitai.common import llm
from pygitai.common.config import config
from pygitai.common.exceptions import (
    InvalidRole,
    JobImproperlyConfigured,
    NoJobConfigured,
)
from pygitai.common.llm.base import LLMBase, PromptLine
from pygitai.common.logger import get_logger
from pygitai.common.utils import camel_to_snake, load_template_file

logger = get_logger(__name__, config.logger.level)


T = TypeVar("T")


class JobBase(ABC, Generic[T]):
    """Base class for Job.

    A Job will always be executed as part of a pipeline.

    The generic type `T` in this class represents the type of the
    result that the job produces in it's `perform` method. For
    instance, if a job is responsible for processing data and
    returning a list of results, `T` could be `List[ResultType]`.
    If the job doesn't return any meaningful value, `T` could
    be `None`.

    Attributes:
    -----------
    cli_configurable_name:
        The name of the attribute in the cli args that will be used
        to determine if this job should be executed. Only boolean
        values are supperted at the moment. If it is None, the
        job will always be executed.
    cli_args:
        The cli arguments.
    kwargs:
        The keyword arguments that were passed to the job.
    """

    cli_configurable_name: str | None = None

    def perform(self, cli_args: Namespace, *args, **kwargs) -> T | None:
        """Perform the job. This method is just a wrapper around
        `exec_command`. It's used to determine if the job should be
        executed or not.

        Argsuments:
        -----------
        cli_args:
            The cli arguments. Those arguments will be bound to the
            job instance.
        """
        self.cli_args = cli_args
        self.kwargs = kwargs

        if self.cli_configurable_name and self.cli_configurable_name not in cli_args:
            return None
        elif self.cli_configurable_name and not getattr(
            cli_args, self.cli_configurable_name
        ):
            # getattr will raise an Error if the attribute is not found
            # that's why there are seperate if statements
            return None
        else:
            return self.exec_command(*args, **kwargs)

    @abstractmethod
    def exec_command(self, *args, **kwargs) -> T:
        """Execute the command"""
        pass


def ask_for_user_feedback(prompt_output_context: str, prompt_output: str) -> str:
    """Ask the user for feedback.

    This is an interactive terminal method.


    Arguments:
    ----------
    prompt_output_context:
        The current context of the prompt output, i.e. `commit_title`.
    prompt_output:
        The AI response.


    Returns:
    --------
    The user feedback. It can be either `y` or a recommendation for a
    better output (i.e. `Add a dot at the end of the sentence`) and
    it can be empty if the user doesn't want to provide any feedback.
    """
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


class LLMJobBase(JobBase[T]):
    """Base class for LLMJob. This kind of job should be used if an
    interaction with a LLM is required.

    Attributes:
    -----------
    llm:
        The LLM API that should be used. If it's none the default
        LLM API or the specified LLM API in the config will be used.
    llm_model:
        The LLM model that should be used. If it's none the default
        LLM model or the specified LLM model in the config will be
        used.
    template_file:
        The path to the template file that should be used. If it's
        none the default template file or the specified template file
        will be used.
    """

    llm: Type[LLMBase] | None = None
    llm_model: str | None = None
    template_file: Path | str | None = None

    @property
    def context(self) -> str:
        """Get the context of the job.

        The context is used to determine the template file that
        should be used and will prefix some logs.

        The context is determined by the class name of the job.


        Returns:
        --------
        The context of the job in snake_case.


        Examples:
        ---------
        >>> class MyJob(LLMJobBase):
        ...     pass
        ...
        >>> MyJob().context
        'my_job'
        >>> class MyLLMJob(LLMJobBase):
        ...     pass
        ...
        >>> MyLLMJob().context
        'my_llm_job'
        """
        return camel_to_snake(self.__class__.__name__)

    def get_llm_initial_message(
        self,
        context_system: dict | None = None,
        context_user: dict | None = None,
    ):
        """Get the initial message from the LLM.

        This method will use the template files to generate the
        initial message. The template files will be determined by the
        `context` of the job.

        A prompt consists of two parts: The system part and the user
        part. The system part just contains generic information about
        the context. The user part contains the information that is
        specific to the user (i.e. current code changes).

        This method will be always used to start a conversation with
        the LLM.

        Arguments:
        ----------
        context_system:
            Additional context which will be passed to the template
            file for the system
        context_user:
            Additional context which will be passed to the template
            file for the user


        Returns:
        --------
        The initial prompt for the LLM to deal with.
        """
        content_system = load_template_file(
            template_path=self.get_template_file(type_="system"),
            context=context_system or {},
        )
        content_user = load_template_file(
            template_path=self.get_template_file(type_="user"),
            context=context_user or {},
        )
        prompt = self.get_llm_klass().llm_parser.parse_prompt(
            input_data=(
                PromptLine(role="system", text=content_system),
                PromptLine(role="user", text=content_user),
            )
        )
        return prompt

    def get_llm_response(
        self,
        context_system: dict | None = None,
        context_user: dict | None = None,
        prompt_override: list = None,
    ) -> tuple:
        """Get the response from the LLM.

        This method will use a LLM API and execute a prompt. The
        response of the LLM will be returned.

        The prompt will be generated by the `get_llm_initial_message`
        method.

        Arguments:
        ----------
        context_system:
            Additional context which will be passed to the template
            file for the system
        context_user:
            Additional context which will be passed to the template
            file for the user
        prompt_override:
            This argument can be set if there is an already existing
            prompt or conversation which should be continued. If
            it's None the prompt will be generated by the
            `get_llm_initial_message` method.


        Returns:
        --------
        The response from the LLM and the full context of the prompt
        that was sent to the LLM.


        Examples:
        ---------
        >>> class MyLLMJob(LLMJobBase):
        ...     pass
        ...
        >>> response, full_context = MyLLMJob().get_llm_response()
        >>> response
        'This is a response.'
        >>> full_context
        [
            {
                'role': 'system',
                'content': 'This is a multiline prompt.'
            },
            {
                'role': 'user',
                'content': 'This is a second line.'
            },
            {
                'role': 'user',
                'content': 'And another part of the conversation.'
            },
            {
                'role': 'assistant',
                'content': 'This is a response.'
            }
        ]
        """
        prompt = prompt_override or self.get_llm_initial_message(
            context_system=context_system or {},
            context_user=context_user or {},
        )
        return self.get_llm_klass().exec_prompt(
            prompt=prompt,
            model=self.get_llm_model(),
        )

    def process_user_feedback_llm_loop(
        self,
        context: str,
        context_user: dict | None = None,
        context_system: dict | None = None,
    ):
        """Process user llm interaction in an infinite loop.

        This method is an interactive terminal method. It's
        moderating the interaction between the user and the LLM until
        the user is satisfied with the output.


        Arguments:
        ----------
        context:
            The context of the interaction. This will be used to
            determine the template file that should be used.
            This argument will be deprecated in the future - it's
            already determined by the class property `context`.
        context_system:
            Additional context which will be passed to the template
            file for the system
        context_user:
            Additional context which will be passed to the template
            file for the user


        Returns:
        --------
        The final response from the LLM.
        """
        prompt_override = None
        user_feedback = None
        while user_feedback != "y":
            prompt_output, prompt_output_full_context = self.get_llm_response(
                prompt_override=prompt_override,
                context_user=context_user or {},
                context_system=context_system or {},
            )
            user_feedback = ask_for_user_feedback(
                prompt_output_context=context,
                prompt_output=prompt_output,
            )
            if user_feedback != "y":
                revision_prompt = load_template_file(
                    template_path=self.get_template_file(type_="revision"),
                    context={"feedback": user_feedback or "No further info provided"},
                )
                prompt_override = (
                    prompt_output_full_context
                    + self.get_llm_klass().llm_parser.parse_prompt(
                        input_data=(PromptLine(role="system", text=revision_prompt),)
                    )
                )
        return prompt_output

    def get_llm_klass(self) -> Type[LLMBase]:
        """Get the LLM API that should be used.

        This method will use the `llm_api` attribute of the job
        instance. If it's not set, the default LLM API or the
        specified LLM API in the config will be used.


        Returns:
        --------
        The LLM API that should be used. e.g. OpenAI, HuggingFace,
        etc.


        Raises:
        -------
        NoJobConfigured:
            If no LLM API is configured for the job. This can happen
            if the `default_llm_api` was removed from the config and
            the job doesn't specify a LLM API.
        """
        if self.llm is not None:
            return self.llm

        llm_api_name = None
        cfg_ = config.general.cfg
        if f"pygitai.jobs.{self.__class__.__name__}" in cfg_:
            llm_api_name = cfg_[f"pygitai.jobs.{self.__class__.__name__}"].get(
                "llm_api"
            )
        if not llm_api_name:
            llm_api_name = cfg_["pygitai"].get("default_llm_api")
        if not llm_api_name:
            raise NoJobConfigured(
                f"No LLM API configured for job {self.__class__.__name__}"
            )
        return getattr(llm, llm_api_name)

    def get_llm_model(self) -> str:
        """Get the LLM model that should be used.

        This method will use the `llm_model` attribute of the job
        instance. If it's not set, the default LLM model or the
        specified LLM model in the config will be used.


        Returns:
        --------
        The LLM model that should be used. e.g. davinci, gpt-3.5-turbo,
        etc.


        Raises:
        -------
        NoJobConfigured:
            If no LLM model is configured for the job. This can happen
            if the `default_llm_model` was removed from the config and
            the job doesn't specify a LLM model.
        """
        cfg_ = config.general.cfg
        llm_model = None
        if f"pygitai.jobs.{self.__class__.__name__}" in cfg_:
            return cfg_[f"pygitai.jobs.{self.__class__.__name__}"].get("llm_model")
        if not llm_model:
            return cfg_["pygitai"].get("default_llm_model")
        else:
            raise JobImproperlyConfigured(
                f"No LLM Model configured for job {self.__class__.__name__}"
            )

    def get_template_file(self, type_: str) -> Path:
        """Get the template file that should be used.

        This method will use the `template_file` attribute of the job
        instance. If it's not set, the default template file or the
        specified template file in the config will be used.

        Arguments:
        ----------
        type_:
            The type of the template file. This will be
            used to determine the template file name. Allowed
            values are: system, user, revision


        Returns:
        --------
        The template file that should be used.


        Raises:
        -------
        NoJobConfigured:
            If no template file is configured for the job. This can
            happen if the `default_prompt_template_dir` was removed
            from the config and the job doesn't specify a template
            file.
        InvalidRole:
            If the type of the template file is not valid.
        """
        if type_ not in ["system", "user", "revision"]:
            raise InvalidRole(
                f"Invalid role {type_} for template file. "
                "Allowed values are: `system`, `user`, `revision`"
            )
        if self.template_file is not None:
            if isinstance(self.template_file, Path):
                return self.template_file
            return Path(self.template_file)

        template_file_path = None
        template_dir = None
        template_file_name = f"{self.context}_{type_}.jinja2"
        cfg_ = config.general.cfg

        if f"pygitai.jobs.{self.__class__.__name__}" in cfg_:
            template_dir = cfg_[f"pygitai.jobs.{self.__class__.__name__}"].get(
                "prompt_template_dir"
            )

        if not template_file_path:
            template_dir = cfg_["pygitai"].get("default_prompt_template_dir")

        if not template_dir:
            raise NoJobConfigured(
                f"No LLM API configured for job {self.__class__.__name__}"
            )

        template_dir_path = config.general.toplevel_directory / Path(template_dir)
        template_file_path = template_dir_path / template_file_name
        if not template_file_path.exists():
            raise JobImproperlyConfigured(
                f"No template file configured for job {self.__class__.__name__}"
            )

        return template_file_path

    def exec_command(self, *args, **kwargs):
        """Execute the command"""
        raise NotImplementedError
