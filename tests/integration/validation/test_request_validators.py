from base64 import b64encode

import pytest

from openapi_core import V30RequestValidator
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.testing import MockRequest
from openapi_core.validation.request.exceptions import MissingRequiredParameter
from openapi_core.validation.request.exceptions import (
    RequestBodyValidationError,
)
from openapi_core.validation.request.exceptions import SecurityValidationError


class TestRequestValidator:
    host_url = "http://petstore.swagger.io"

    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    @pytest.fixture(scope="session")
    def spec_dict(self, v30_petstore_content):
        return v30_petstore_content

    @pytest.fixture(scope="session")
    def spec(self, v30_petstore_spec):
        return v30_petstore_spec

    @pytest.fixture(scope="session")
    def request_validator(self, spec):
        return V30RequestValidator(spec)

    def test_request_server_error(self, request_validator):
        request = MockRequest("http://petstore.invalid.net/v1", "get", "/")

        with pytest.raises(PathNotFound):
            request_validator.validate(request)

    def test_path_not_found(self, request_validator):
        request = MockRequest(self.host_url, "get", "/v1")

        with pytest.raises(PathNotFound):
            request_validator.validate(request)

    def test_operation_not_found(self, request_validator):
        request = MockRequest(self.host_url, "patch", "/v1/pets")

        with pytest.raises(OperationNotFound):
            request_validator.validate(request)

    def test_missing_parameter(self, request_validator):
        request = MockRequest(self.host_url, "get", "/v1/pets")

        with pytest.raises(MissingRequiredParameter):
            with pytest.warns(DeprecationWarning):
                request_validator.validate(request)

    def test_security_not_found(self, request_validator):
        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets/1",
            path_pattern="/v1/pets/{petId}",
            view_args={"petId": "1"},
        )

        with pytest.raises(SecurityValidationError) as exc_info:
            request_validator.validate(request)

        assert exc_info.value.__cause__ == SecurityNotFound(
            [["petstore_auth"]]
        )

    def test_media_type_not_found(self, request_validator):
        data = b"csv,data"
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }
        request = MockRequest(
            "https://development.gigantic-server.com",
            "post",
            "/v1/pets",
            path_pattern="/v1/pets",
            content_type="text/csv",
            data=data,
            headers=headers,
            cookies=cookies,
        )

        with pytest.raises(RequestBodyValidationError) as exc_info:
            request_validator.validate(request)

        assert exc_info.value.__cause__ == MediaTypeNotFound(
            mimetype="text/csv",
            availableMimetypes=[
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain",
            ],
        )

    def test_valid(self, request_validator):
        authorization = "Basic " + self.api_key_encoded
        headers = {
            "Authorization": authorization,
        }
        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets/1",
            path_pattern="/v1/pets/{petId}",
            view_args={"petId": "1"},
            headers=headers,
        )

        result = request_validator.validate(request)

        assert result is None
