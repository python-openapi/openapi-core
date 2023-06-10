import pytest

from openapi_core.contrib.aiohttp.requests import AIOHTTPOpenAPIWebRequest


class TestAIOHTTPOpenAPIWebRequest:
    def test_type_invalid(self):
        with pytest.raises(TypeError):
            AIOHTTPOpenAPIWebRequest(None)
