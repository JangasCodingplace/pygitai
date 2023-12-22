from pygitai.common.utils import camel_to_snake, load_template_file
from tests import FIXTURES_DIR


class TestCamelToSnakeCase:
    def test_snake_to_snake(self):
        assert camel_to_snake("snake_case") == "snake_case"

    def test_simple_camel_to_snake(self):
        assert camel_to_snake("CamelCase") == "camel_case"

    def test_uppercase_chain_to_snake(self):
        assert camel_to_snake("ABCOther") == "abc_other"


class TestLoadTemplateFile:
    def test_template_file_without_context(self):
        template_file = (
            FIXTURES_DIR / "templates" / "test_template_without_context.jinja2"
        )
        expected_template = "This is a test template without any context."
        assert load_template_file(template_file, {}) == expected_template

    def test_template_file_with_context(self):
        template_file = FIXTURES_DIR / "templates" / "test_template_with_context.jinja2"
        context = {
            "testcase_name": "TestLoadTemplateFile.test_template_file_with_context"
        }
        expected_template = (
            "This is a test template.\n\n" f"Test case name: {context['testcase_name']}"
        )
        assert load_template_file(template_file, context) == expected_template
