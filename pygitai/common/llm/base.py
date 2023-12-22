from dataclasses import dataclass
from typing import Generic, Type, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


@dataclass
class PromptLine:
    """A Single prompt line

    Attributes:
        role: The role of the line (e.g. "user" or "system")
        text: The text of the line
    """

    role: str
    text: str


class ParserBase(Generic[T, U, W]):
    """Base class LLM parser. This is used to parse the response from
    the language model and to create the prompt for the LLM API.
    """

    @staticmethod
    def parse_response(response: T, prompt: U | None = None) -> W:
        """Parse the response from the language model into a format
        and type to continue to work with.

        Args:
            response: The response from the language model
            promp: (optional) The prompt which was used to generate
                the response.

        Returns:
            The parsed response
        """
        raise NotImplementedError

    @staticmethod
    def parse_prompt(input_data: tuple[PromptLine, ...]) -> U:
        """Parse a generic code object into a specific prompt object
        which will be sent to the llm.

        Args:
            input_data: The input data to parse

        Returns:
            The parsed prompt which can be sent to the llm.
        """
        raise NotImplementedError


class LLMBase(Generic[U, V]):
    """Base class for all language models

    Attributes:
        llm_parser: The parser for the language model. This is used
            to parse the response from the language model and to
            create the prompt for the LLM API.
    """

    llm_parser: Type[ParserBase]

    @classmethod
    def get_input_token_count(cls, prompt: U) -> int:
        """Return the number of tokens in the prompt"""
        raise NotImplementedError

    @classmethod
    def exec_prompt(cls, prompt: U, model: str) -> tuple[V, U]:
        """Execute a prompt and return the result

        Args:
            prompt: The parsed prompt to execute
            model: The model to use for the prompt
        """
        raise NotImplementedError
