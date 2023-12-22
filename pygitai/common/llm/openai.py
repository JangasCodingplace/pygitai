import requests

from pygitai.common.config import config
from pygitai.common.logger import get_logger

from .base import LLMBase, ParserBase, PromptLine

logger = get_logger(__name__, config.logger.level)


class OpenAIParser(ParserBase[requests.Response, list, str]):
    @staticmethod
    def parse_response(response: requests.Response, prompt: list | None = None) -> str:
        """Parse the response from OpenAI


        Arguments:
        ----------
        response:
            The response from OpenAI API.
        prompt:
            The prompt that was used to generate the response.
            This might be useful for debugging.


        Returns:
        --------
        The parsed response from OpenAI API.
        """
        return response.json()["choices"][0]["message"]["content"]

    @staticmethod
    def parse_prompt(input_data: tuple[PromptLine, ...] | PromptLine):
        """Parse the input data and return a list of dict.


        Arguments:
        ----------
        input_data:
            The input data to parse. It can be a single PromptLine
            or a tuple of PromptLine.


        Returns:
        --------
        A list of dict with the following format:
        [
            {
                "role": <ROLE_NAME>,
                "content": <CONTENT>,
            },
        ]


        Example:
        --------
        >>> prompt_line = PromptLine(
        ...     role="user", text="This is a one way prompt."
        ... )
        >>> OpenAIParser.parse_prompt(prompt_line)
        [{'role': 'user', 'content': 'This is a one way prompt.'}]
        >>> prompt_lines = (
        ...     PromptLine(role="system", text="This is a multiline prompt.",),
        ...     PromptLine(role="user", text="This is a second line.",),
        ...     PromptLine(role="user", text="And another part of the conversation.",),
        ...     PromptLine(role="assistant", text="This is a response.",),
        ... )
        >>> OpenAIParser.parse_prompt(prompt_lines)
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
        if isinstance(input_data, PromptLine):
            input_data = (input_data,)
        return [
            {
                "role": row.role,
                "content": row.text,
            }
            for row in input_data
        ]


class OpenAI(LLMBase[list, str]):
    config = config.openai
    llm_parser = OpenAIParser

    @classmethod
    def get_prompt_token_count(cls, prompt):
        """Return the number of tokens in the prompt
        This method is created based on OpenAIs article:
        https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them  # noqa
        """
        prompt_ = " ".join([row["content"] for row in prompt])
        return len(prompt_) // 4

    @classmethod
    def exec_prompt(cls, prompt, model):
        """Execute a prompt and return the result"""
        calculated_token_count = cls.get_prompt_token_count(prompt)
        logger.info(f"Token input count: {calculated_token_count}")
        if calculated_token_count > cls.config.openai_api_token_limit:
            raise ValueError(
                f"Token count {calculated_token_count} exceeds the limit of "
                f"{cls.config.openai_api_token_limit}"
            )
        payload = {
            "model": model,
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
        logger.info(f"Real Prompt token: {response.json()['usage']['prompt_tokens']}")
        logger.info(f"Total token: {response.json()['usage']['total_tokens']}")
        logger.debug(f"OpenAI response: {response.json()}")
        parsed_llm_response = cls.llm_parser.parse_response(
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
