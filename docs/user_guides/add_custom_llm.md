# Add a Custom LLM

## Quickstart

Use the following command to create an empty llm template:
```
pygitai customization --type llm --name MyLLM
```

This will create a new llm file into
`.pygitai/pygitai_customization/llm` including the classes:

- `MyLLM`
- `MyLLMParser`

For more information about the classes refer to the following API
docs:

- [LLMBase](../api/LLMBase.md)
- [ParserBase](../api/ParserBase.md)
- [PromptLine](../api/PromptLine.md)

## Example

```python
# Add this class to the .pygitai/pygitai_customization/llm directory
from pygitai.common.llm.base import LLMBase, ParserBase, PromptLine


class MyLLMParser(ParserBase):
    @staticmethod
    def parse_response(response, prompt):
        # To be implemented
        pass

    @staticmethod
    def parse_prompt(input_data):
        # To be implemented
        pass


class MyLLM(LLMBase):
    llm_parser = MyLLMParser

    @classmethod
    def exec_prompt(cls, prompt, model):
        # To be implemented
        pass
```

