import pytest

from openapi_core.contrib.aiohttp.responses import AIOHTTPOpenAPIWebResponse


class TestAIOHTTPOpenAPIWebResponse:
    def test_type_invalid(self):
        with pytest.raises(TypeError):
            AIOHTTPOpenAPIWebResponse(None)
