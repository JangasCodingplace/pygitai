from typing import Generic, Type, TypeVar

import requests

from .config import OpenAIConfig, config
from .logger import get_logger

logger = get_logger(__name__, config.logger.level)


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


class ResponseParserBase(Generic[T, U, W]):
    @staticmethod
    def parse(response: T, prompt: U) -> tuple[W]:
        raise NotImplementedError


class LLMBase(Generic[U, V]):
    llm_response_parser: Type[ResponseParserBase]

    @classmethod
    def exec_prompt(cls, prompt: U) -> tuple[V, U]:
        """Execute a prompt and return the result"""
        raise NotImplementedError


class OpenAI(LLMBase[list, str]):
    config: OpenAIConfig
    llm_response_parser: Type[ResponseParserBase[requests.Response, list, str]]

    @classmethod
    def exec_prompt(cls, prompt):
        """Execute a prompt and return the result"""
        payload = {
            "model": cls.config.openai_model,
            "messages": prompt,
        }
        logger.info("Wait for openai response")
        logger.debug(f"Send Payload to OpenAI: {payload}")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {cls.config.openai_key_secret}",
            },
            json=payload,
        )
        response.raise_for_status()
        logger.info("OpenAI response received")
        logger.debug(f"OpenAI response: {response.json()}")
        parsed_llm_response = cls.llm_response_parser.parse(
            prompt=prompt,
            response=response,
        )
        full_context = prompt + [
            {
                "role": "assistant",
                "content": parsed_llm_response,
            },
        ]
        return parsed_llm_response, full_context
