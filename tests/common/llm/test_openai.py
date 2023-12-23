import json
from functools import partial

import pytest
import requests

from pygitai.common.llm import openai


class TestOpenAIParser:
    def test_parse_single_prompt(self):
        prompt_line = openai.PromptLine(role="user", text="This is a one way prompt.")
        expected_prompt = [
            {
                "role": prompt_line.role,
                "content": prompt_line.text,
            }
        ]
        assert openai.OpenAIParser.parse_prompt(prompt_line) == expected_prompt

    def test_parse_multiline_prompt(self):
        prompt_lines = (
            openai.PromptLine(
                role="system",
                text="This is a multiline prompt.",
            ),
            openai.PromptLine(
                role="user",
                text="This is a second line.",
            ),
            openai.PromptLine(
                role="user",
                text="And another part of the conversation.",
            ),
            openai.PromptLine(
                role="assistant",
                text="This is a response.",
            ),
        )
        expected_prompt = [
            {
                "role": row.role,
                "content": row.text,
            }
            for row in prompt_lines
        ]
        assert openai.OpenAIParser.parse_prompt(prompt_lines) == expected_prompt

    def test_parse_response(self):
        content = "It's a test response"
        response = requests.Response()
        response._content = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": content,
                        },
                    }
                ]
            }
        ).encode()
        assert openai.OpenAIParser.parse_response(response) == content


class TestOpenAI:
    def setup_class(self):
        self.line_1 = "This is a test string."
        self.line_2 = "This is another test string."
        self.prompt = [
            {"role": "user", "content": self.line_1},
            {"role": "user", "content": self.line_2},
        ]

    def mock_get_prompt_token_count(self, prompt):
        return sum([len(row["content"]) for row in prompt]) // 4

    def mock_parse_response(self, response, prompt, mocked_return_value):
        return mocked_return_value

    class MockRequests:
        @classmethod
        def post(cls, mocked_response, *args, **kwargs):
            return mocked_response

    def test_get_prompt_token_count(self, monkeypatch):
        expected_token_count = (len(self.line_1) + len(self.line_2)) // 4
        assert openai.OpenAI.get_prompt_token_count(self.prompt) == expected_token_count

    def test_exec_prompt_success(self, monkeypatch):
        expected_token_count = (len(self.line_1) + len(self.line_2)) // 4
        response_content = "It's a test response"

        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps(
            {
                "usage": {
                    "prompt_tokens": int(expected_token_count * 0.25),
                    "total_tokens": (
                        int(expected_token_count * 0.25) + len(response_content) // 4
                    ),
                },
                "choices": [
                    {
                        "message": {
                            "content": response_content,
                        },
                    }
                ],
            }
        ).encode()

        monkeypatch.setattr(
            openai.OpenAI,
            "get_prompt_token_count",
            self.mock_get_prompt_token_count,
        )
        monkeypatch.setattr(
            openai.requests,
            "post",
            partial(self.MockRequests.post, response),
        )
        monkeypatch.setattr(
            openai.OpenAIParser,
            "parse_response",
            partial(self.mock_parse_response, mocked_return_value=response_content),
        )

        assert openai.OpenAI.exec_prompt(self.prompt, model="test-gpt-3.5") == (
            response_content,
            self.prompt + [{"role": "assistant", "content": response_content}],
        )

    def test_exec_prompt_failure_on_max_token(self, monkeypatch):
        class ConfigPatch:
            openai_api_token_limit = 0

        monkeypatch.setattr(
            openai.OpenAI,
            "get_prompt_token_count",
            self.mock_get_prompt_token_count,
        )
        monkeypatch.setattr(
            openai.OpenAI,
            "config",
            ConfigPatch,
        )
        with pytest.raises(ValueError):
            openai.OpenAI.exec_prompt(self.prompt, model="test-gpt-3.5")

    def test_exec_prompt_failure_on_response(self, monkeypatch):
        response = requests.Response()
        response.status_code = 401
        response._content = json.dumps({}).encode()

        monkeypatch.setattr(
            openai.OpenAI,
            "get_prompt_token_count",
            self.mock_get_prompt_token_count,
        )
        monkeypatch.setattr(
            openai.requests,
            "post",
            partial(self.MockRequests.post, response),
        )
        with pytest.raises(requests.exceptions.HTTPError):
            openai.OpenAI.exec_prompt(self.prompt, model="test-gpt-3.5")
