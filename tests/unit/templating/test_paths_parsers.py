import pytest

from openapi_core.templating.paths.parsers import PathParser


class TestSearch:
    def test_endswith(self):
        path_pattern = "/{test}/test"
        parser = PathParser(path_pattern, post_expression="$")
        full_url_pattern = "/test1/test/test2/test"

        result = parser.search(full_url_pattern)

        assert result.named == {
            "test": "test2",
        }

    def test_exact(self):
        path_pattern = "/{test}/test"
        parser = PathParser(path_pattern, post_expression="$")
        full_url_pattern = "/test/test"

        result = parser.search(full_url_pattern)

        assert result.named == {
            "test": "test",
        }

    @pytest.mark.parametrize(
        "path_pattern,expected",
        [
            ("/{test_id}/test", {"test_id": "test"}),
            ("/{test.id}/test", {"test.id": "test"}),
            ("/{test-id}/test", {"test-id": "test"}),
        ],
    )
    def test_chars_valid(self, path_pattern, expected):
        parser = PathParser(path_pattern, post_expression="$")
        full_url_pattern = "/test/test"

        result = parser.search(full_url_pattern)

        assert result.named == expected

    @pytest.mark.xfail(
        reason=(
            "Special characters of regex not supported. "
            "See https://github.com/python-openapi/openapi-core/issues/672"
        ),
        strict=True,
    )
    @pytest.mark.parametrize(
        "path_pattern,expected",
        [
            ("/{test~id}/test", {"test~id": "test"}),
        ],
    )
    def test_special_chars_valid(self, path_pattern, expected):
        parser = PathParser(path_pattern, post_expression="$")
        full_url_pattern = "/test/test"

        result = parser.search(full_url_pattern)

        assert result.named == expected
