from pygitai.common.git import file_name_matches_patterns, get_ignored_file_patterns


class TestGetIgnoredFilePatterns:
    def test_get_ignored_file_patterns_ignore_exists(self):
        expected_patterns = [
            "poetry.lock",
        ]
        assert get_ignored_file_patterns() == expected_patterns


class TestFileMatchesPatterns:
    def test_file_matches_patterns_match(self):
        assert file_name_matches_patterns("poetry.lock", ["poetry.lock"])

    def test_file_matches_patterns_match_wildcard(self):
        assert file_name_matches_patterns("poetry.lock", ["*.lock"])

    def test_file_matches_patterns_no_match(self):
        assert not file_name_matches_patterns("poetry.lock", ["*.toml"])
