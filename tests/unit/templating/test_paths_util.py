from openapi_core.templating.paths.util import path_qs


class TestPathQs(object):

    def test_path(self):
        url = 'https://test.com:1234/path'

        result = path_qs(url)

        assert result == '/path'

    def test_query(self):
        url = 'https://test.com:1234/path?query=1'

        result = path_qs(url)

        assert result == '/path?query=1'
