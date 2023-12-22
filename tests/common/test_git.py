from pygitai.common.git import get_ignored_file_patterns


class TestGetIgnoredFilePatterns:
    def test_get_ignored_file_patterns_ignore_exists(self):
        expected_patterns = [
            "poetry.lock",
        ]
        assert get_ignored_file_patterns() == expected_patterns
