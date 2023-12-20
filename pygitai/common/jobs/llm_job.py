from pathlib import Path
from typing import Type

import jinja2

from pygitai.common import llm
from pygitai.common.config import config
from pygitai.common.llm.base import LLMBase, PromptLine
from pygitai.common.logger import get_logger
from pygitai.common.utils import camel_to_snake

from .base_job import BaseJob

logger = get_logger(__name__, config.logger.level)


class NoJobConfigured(Exception):
    """No job configured"""


class ImproperlyConfigured(Exception):
    """Improperly configured"""


def get_prompt_from_template(
    template_path: Path,
    context: dict,
) -> str:
    """Get the prompt from the template"""
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent)
    )
    file_name = template_path.name
    template = template_env.get_template(file_name)
    return template.render(**context)


def ask_for_user_feedback(prompt_output_context: str, prompt_output: str):
    """Ask the user for feedback"""
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


class LLMJobBase(BaseJob):
    """Base class for LLMJob"""

    job_name: str | None = None
    llm: Type[LLMBase] | None = None
    llm_model: str | None = None
    template_file: Path | str | None = None

    @property
    def context(self):
        return camel_to_snake(self.__class__.__name__)

    def get_llm_initial_message(
        self,
        context_system: dict | None = None,
        context_user: dict | None = None,
    ):
        """Get the initial message from the LLM"""
        content_system = get_prompt_from_template(
            template_path=self.get_template_file(type_="system"),
            context=context_system or {},
        )
        content_user = get_prompt_from_template(
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
    ):
        """Get the response from the LLM"""
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
                revision_prompt = get_prompt_from_template(
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
        cfg_ = config.general.cfg
        llm_model = None
        if f"pygitai.jobs.{self.__class__.__name__}" in cfg_:
            return cfg_[f"pygitai.jobs.{self.__class__.__name__}"].get("llm_model")
        if not llm_model:
            return cfg_["pygitai"].get("default_llm_model")
        else:
            raise ImproperlyConfigured(
                f"No LLM Model configured for job {self.__class__.__name__}"
            )

    def get_template_file(self, type_: str) -> Path:
        if self.template_file is not None:
            if isinstance(self.template_file, Path):
                return self.template_file
            return Path(self.template_file)

        template_file_path = None
        template_dir = None
        template_file_name = f"{self.context}_{type_}.txt"
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
            raise ImproperlyConfigured(
                f"No template file configured for job {self.__class__.__name__}"
            )

        return template_file_path

    def exec_command(self, *args, **kwargs):
        raise NotImplementedError
