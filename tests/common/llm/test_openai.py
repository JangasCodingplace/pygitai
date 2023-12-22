import json

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
    def test_get_prompt_token_count(self):
        line_1 = "This is a test string."
        line_2 = "This is another test string."
        s = [
            {"role": "user", "content": line_1},
            {"role": "user", "content": line_2},
        ]
        expected_token_count = (len(line_1) + len(line_2)) // 4
        assert openai.OpenAI.get_prompt_token_count(s) == expected_token_count
