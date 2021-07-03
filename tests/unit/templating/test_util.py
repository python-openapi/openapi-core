from openapi_core.templating.util import search


class TestSearch:
    def test_endswith(self):
        path_patter = "/{test}/test"
        full_url_pattern = "/test1/test/test2/test"

        result = search(path_patter, full_url_pattern)

        assert result.named == {
            "test": "test2",
        }

    def test_exact(self):
        path_patter = "/{test}/test"
        full_url_pattern = "/test/test"

        result = search(path_patter, full_url_pattern)

        assert result.named == {
            "test": "test",
        }
