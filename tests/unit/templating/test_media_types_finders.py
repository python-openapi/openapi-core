import pytest

from openapi_core.spec.paths import Spec
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.media_types.finders import MediaTypeFinder
from openapi_core.testing import MockResponse


class TestMediaTypes:
    @pytest.fixture(scope="class")
    def spec(self):
        return {
            "application/json": {"schema": {"type": "object"}},
            "text/*": {"schema": {"type": "object"}},
        }

    @pytest.fixture(scope="class")
    def content(self, spec):
        return Spec.from_dict(spec, validator=None)

    @pytest.fixture(scope="class")
    def finder(self, content):
        return MediaTypeFinder(content)

    def test_exact(self, finder, content):
        mimetype = "application/json"

        _, mimetype = finder.find(mimetype)
        assert mimetype == "application/json"

    def test_match(self, finder, content):
        mimetype = "text/html"

        _, mimetype = finder.find(mimetype)
        assert mimetype == "text/*"

    def test_not_found(self, finder, content):
        mimetype = "unknown"

        with pytest.raises(MediaTypeNotFound):
            finder.find(mimetype)

    def test_missing(self, finder, content):
        mimetype = None

        with pytest.raises(MediaTypeNotFound):
            finder.find(mimetype)
