from base64 import b64encode

import pytest
from six import text_type

from openapi_core.shortcuts import create_spec
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.testing import MockRequest


@pytest.fixture
def request_validator(spec):
    return RequestValidator(spec)


@pytest.fixture('class')
def spec(factory):
    spec_dict = factory.spec_from_file("data/v3.0/security_override.yaml")
    return create_spec(spec_dict)


class TestSecurityOverride(object):

    host_url = 'http://petstore.swagger.io'

    api_key = '12345'

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode('utf8')
        api_key_bytes_enc = b64encode(api_key_bytes)
        return text_type(api_key_bytes_enc, 'utf8')

    def test_default(self, request_validator):
        args = {'api_key': self.api_key}
        request = MockRequest(
            self.host_url, 'get', '/resource/one', args=args)

        result = request_validator.validate(request)

        assert not result.errors
        assert result.security == {
            'api_key': self.api_key,
        }

    def test_default_invalid(self, request_validator):
        request = MockRequest(self.host_url, 'get', '/resource/one')

        result = request_validator.validate(request)

        assert type(result.errors[0]) == InvalidSecurity
        assert result.security is None

    def test_override(self, request_validator):
        authorization = 'Basic ' + self.api_key_encoded
        headers = {
            'Authorization': authorization,
        }
        request = MockRequest(
            self.host_url, 'post', '/resource/one', headers=headers)

        result = request_validator.validate(request)

        assert not result.errors
        assert result.security == {
            'petstore_auth': self.api_key_encoded,
        }

    def test_override_invalid(self, request_validator):
        request = MockRequest(
            self.host_url, 'post', '/resource/one')

        result = request_validator.validate(request)

        assert type(result.errors[0]) == InvalidSecurity
        assert result.security is None

    def test_remove(self, request_validator):
        request = MockRequest(
            self.host_url, 'put', '/resource/one')

        result = request_validator.validate(request)

        assert not result.errors
        assert result.security == {}
