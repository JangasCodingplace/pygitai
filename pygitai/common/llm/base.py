from dataclasses import dataclass
from typing import Generic, Type, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


@dataclass
class PromptLine:
    role: str
    text: str


class ParserBase(Generic[T, U, W]):
    @staticmethod
    def parse_response(response: T, prompt: U) -> W:
        raise NotImplementedError

    @staticmethod
    def parse_prompt(input_data: tuple[PromptLine, ...]) -> U:
        raise NotImplementedError


class LLMBase(Generic[U, V]):
    llm_parser: Type[ParserBase]

    @classmethod
    def get_input_token_count(cls, prompt: U) -> int:
        """Return the number of tokens in the prompt"""
        raise NotImplementedError

    @classmethod
    def exec_prompt(cls, prompt: U) -> tuple[V, U]:
        """Execute a prompt and return the result"""
        raise NotImplementedError
