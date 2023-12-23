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
    -----------
    role:
        The role of the prompt line. This can be either "user",
        "system" or "assistant".
    text:
        The text of the prompt line.
    """

    role: str
    text: str


class ParserBase(Generic[T, U, W]):
    """Base class for an LLM parser. This class is designed to parse
    the response from the language model (LLM) and create the prompt
    for the LLM API.

    The ParserBase uses generic type hints (T, U, W) to provide
    flexibility in handling different types of inputs and outputs.
    For example, T could be a string representing the raw response
    from the LLM, U could be a structured data type (like a
    dictionary) used for creating prompts, and W could be a custom
    class or data structure that represents the parsed response.

    Examples:
    ---------
    - T could be `str`, representing raw text from the LLM.
    - U could be `Dict[str, Any]`, used for creating structured
        prompts.
    - W could be a custom class, `ParsedResponse`, representing the
        processed output.

    This generic approach allows the parser to be adapted for various
    LLMs and response formats.
    """

    @staticmethod
    def parse_response(response: T, prompt: U | None = None) -> W:
        """Parse the response from the language model into a format
        and type to continue to work with.


        Arguments:
        ----------
        response:
            The response from the language model.
        prompt:
            The prompt that was used to generate the response.
            This might be useful for debugging.


        Returns:
        --------
        The parsed response from the language model.
        """
        raise NotImplementedError

    @staticmethod
    def parse_prompt(input_data: tuple[PromptLine, ...] | PromptLine) -> U:
        """Parse a generic code object into a specific prompt object
        which will be sent to the llm.


        Arguments:
        ----------
        input_data:
            The input data to parse. It can be a single PromptLine
            or a tuple of PromptLine.


        Returns:
        --------
        A specific prompt object to be sent to the llm.
        """
        raise NotImplementedError


class LLMBase(Generic[U, V]):
    """Base class for all language models


    Attributes:
    -----------
    llm_parser:
        The parser for the language model. This is used to parse the
        response from the language model and to create the prompt for
        the LLM API.
    """

    llm_parser: Type[ParserBase]

    @classmethod
    def get_input_token_count(cls, prompt: U) -> int:
        """Return the number of tokens in the prompt


        Arguments:
        ----------
        prompt:
            The prompt to get the token count for.


        Returns:
        --------
        The number of tokens in the prompt.
        """
        raise NotImplementedError

    @classmethod
    def exec_prompt(cls, prompt: U, model: str) -> tuple[V, U]:
        """Execute a prompt and return the result


        Arguments:
        ----------
        prompt:
            The parsed prompt to execute
        model:
            The model to use for the prompt


        Returns:
        --------
        A tuple containing the parsed response from the LLM and the
        """
        raise NotImplementedError
