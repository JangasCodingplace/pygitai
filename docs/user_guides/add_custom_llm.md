# Add a Custom LLM

In many cases, the default LLM provided by pygitai is not enough to
cover all the use cases or company compliance. For this reason,
pygitai provides a simple way to add a custom LLM which maches the
individual needs.

## Quickstart

Use the following command to create an empty llm template:
```
pygitai customization llm --name MyLLM
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

