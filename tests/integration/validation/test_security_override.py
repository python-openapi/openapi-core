from base64 import b64encode

import pytest

from openapi_core import openapi_request_validator
from openapi_core.testing import MockRequest
from openapi_core.validation.exceptions import InvalidSecurity


@pytest.fixture(scope="class")
def spec(factory):
    return factory.spec_from_file("data/v3.0/security_override.yaml")


class TestSecurityOverride:

    host_url = "http://petstore.swagger.io"

    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    def test_default(self, spec):
        args = {"api_key": self.api_key}
        request = MockRequest(self.host_url, "get", "/resource/one", args=args)

        result = openapi_request_validator.validate(spec, request)

        assert not result.errors
        assert result.security == {
            "api_key": self.api_key,
        }

    def test_default_invalid(self, spec):
        request = MockRequest(self.host_url, "get", "/resource/one")

        result = openapi_request_validator.validate(spec, request)

        assert type(result.errors[0]) == InvalidSecurity
        assert result.security is None

    def test_override(self, spec):
        authorization = "Basic " + self.api_key_encoded
        headers = {
            "Authorization": authorization,
        }
        request = MockRequest(
            self.host_url, "post", "/resource/one", headers=headers
        )

        result = openapi_request_validator.validate(spec, request)

        assert not result.errors
        assert result.security == {
            "petstore_auth": self.api_key_encoded,
        }

    def test_override_invalid(self, spec):
        request = MockRequest(self.host_url, "post", "/resource/one")

        result = openapi_request_validator.validate(spec, request)

        assert type(result.errors[0]) == InvalidSecurity
        assert result.security is None

    def test_remove(self, spec):
        request = MockRequest(self.host_url, "put", "/resource/one")

        result = openapi_request_validator.validate(spec, request)

        assert not result.errors
        assert result.security == {}
