from pygitai.common.utils import camel_to_snake


class TestCamelToSnakeCase:
    def test_snake_to_snake(self):
        assert camel_to_snake("snake_case") == "snake_case"

    def test_simple_camel_to_snake(self):
        assert camel_to_snake("CamelCase") == "camel_case"

    def test_uppercase_chain_to_snake(self):
        assert camel_to_snake("ABCOther") == "abc_other"
