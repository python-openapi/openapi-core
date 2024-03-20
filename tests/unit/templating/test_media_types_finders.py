import pytest
from jsonschema_path import SchemaPath

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.media_types.finders import MediaTypeFinder


class TestMediaTypes:
    @pytest.fixture(scope="class")
    def spec(self):
        return {
            "application/json": {"schema": {"type": "object"}},
            "text/*": {"schema": {"type": "object"}},
        }

    @pytest.fixture(scope="class")
    def content(self, spec):
        return SchemaPath.from_dict(spec)

    @pytest.fixture(scope="class")
    def finder(self, content):
        return MediaTypeFinder(content)

    @pytest.mark.parametrize(
        "media_type",
        [
            # equivalent according to RFC 9110
            "text/html;charset=utf-8",
            'Text/HTML;Charset="utf-8"',
            'text/html; charset="utf-8"',
            "text/html;charset=UTF-8",
            "text/html ; charset=utf-8",
        ],
    )
    def test_charset(self, finder, content, media_type):
        mimetype, parameters, _ = finder.find(media_type)
        assert mimetype == "text/*"
        assert parameters == {"charset": "utf-8"}

    def test_exact(self, finder, content):
        mimetype = "application/json"

        mimetype, parameters, _ = finder.find(mimetype)
        assert mimetype == "application/json"
        assert parameters == {}

    def test_match(self, finder, content):
        mimetype = "text/html"

        mimetype, parameters, _ = finder.find(mimetype)
        assert mimetype == "text/*"
        assert parameters == {}

    def test_not_found(self, finder, content):
        mimetype = "unknown"

        with pytest.raises(MediaTypeNotFound):
            finder.find(mimetype)

    def test_missing(self, finder, content):
        mimetype = None

        with pytest.raises(MediaTypeNotFound):
            finder.find(mimetype)
