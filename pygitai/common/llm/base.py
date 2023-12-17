from typing import Generic, Type, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


class ResponseParserBase(Generic[T, U, W]):
    @staticmethod
    def parse(response: T, prompt: U) -> W:
        raise NotImplementedError


class LLMBase(Generic[U, V]):
    llm_response_parser: Type[ResponseParserBase]

    @classmethod
    def get_input_token_count(cls, prompt: U) -> int:
        """Return the number of tokens in the prompt"""
        raise NotImplementedError

    @classmethod
    def exec_prompt(cls, prompt: U) -> tuple[V, U]:
        """Execute a prompt and return the result"""
        raise NotImplementedError
