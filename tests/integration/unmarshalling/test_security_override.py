from base64 import b64encode

import pytest

from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.testing import MockRequest
from openapi_core.unmarshalling.request.unmarshallers import (
    V30RequestUnmarshaller,
)
from openapi_core.validation.request.exceptions import SecurityValidationError


@pytest.fixture(scope="class")
def schema_path(schema_path_factory):
    return schema_path_factory.from_file("data/v3.0/security_override.yaml")


@pytest.fixture(scope="class")
def request_unmarshaller(schema_path):
    return V30RequestUnmarshaller(schema_path)


class TestSecurityOverride:
    host_url = "http://petstore.swagger.io"

    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    def test_default(self, request_unmarshaller):
        args = {"api_key": self.api_key}
        request = MockRequest(self.host_url, "get", "/resource/one", args=args)

        result = request_unmarshaller.unmarshal(request)

        assert not result.errors
        assert result.security == {
            "api_key": self.api_key,
        }

    def test_default_invalid(self, request_unmarshaller):
        request = MockRequest(self.host_url, "get", "/resource/one")

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) is SecurityValidationError
        assert type(result.errors[0].__cause__) is SecurityNotFound
        assert result.security is None

    def test_override(self, request_unmarshaller):
        authorization = "Basic " + self.api_key_encoded
        headers = {
            "Authorization": authorization,
        }
        request = MockRequest(
            self.host_url, "post", "/resource/one", headers=headers
        )

        result = request_unmarshaller.unmarshal(request)

        assert not result.errors
        assert result.security == {
            "petstore_auth": self.api_key_encoded,
        }

    def test_override_invalid(self, request_unmarshaller):
        request = MockRequest(self.host_url, "post", "/resource/one")

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) is SecurityValidationError
        assert type(result.errors[0].__cause__) is SecurityNotFound
        assert result.security is None

    def test_remove(self, request_unmarshaller):
        request = MockRequest(self.host_url, "put", "/resource/one")

        result = request_unmarshaller.unmarshal(request)

        assert not result.errors
        assert result.security == {}
