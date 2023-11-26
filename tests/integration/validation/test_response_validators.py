import json

import pytest

from openapi_core import V30ResponseValidator
from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.responses.exceptions import ResponseNotFound
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.validation.response.exceptions import DataValidationError
from openapi_core.validation.response.exceptions import InvalidData
from openapi_core.validation.response.exceptions import InvalidHeader
from openapi_core.validation.response.exceptions import MissingData
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue


class TestResponseValidator:
    host_url = "http://petstore.swagger.io"

    @pytest.fixture(scope="session")
    def spec_dict(self, v30_petstore_content):
        return v30_petstore_content

    @pytest.fixture(scope="session")
    def spec(self, v30_petstore_spec):
        return v30_petstore_spec

    @pytest.fixture(scope="session")
    def response_validator(self, spec):
        return V30ResponseValidator(spec)

    def test_invalid_server(self, response_validator):
        request = MockRequest("http://petstore.invalid.net/v1", "get", "/")
        response = MockResponse(b"Not Found", status_code=404)

        with pytest.raises(PathNotFound):
            response_validator.validate(request, response)

    def test_invalid_operation(self, response_validator):
        request = MockRequest(self.host_url, "patch", "/v1/pets")
        response = MockResponse(b"Not Found", status_code=404)

        with pytest.raises(OperationNotFound):
            response_validator.validate(request, response)

    def test_invalid_response(self, response_validator):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"Not Found", status_code=409)

        with pytest.raises(ResponseNotFound):
            response_validator.validate(request, response)

    def test_invalid_content_type(self, response_validator):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"Not Found", content_type="text/csv")

        with pytest.raises(DataValidationError) as exc_info:
            response_validator.validate(request, response)

        assert type(exc_info.value.__cause__) == MediaTypeNotFound

    def test_missing_body(self, response_validator):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(None)

        with pytest.raises(MissingData):
            response_validator.validate(request, response)

    def test_invalid_media_type(self, response_validator):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"abcde")

        with pytest.raises(DataValidationError) as exc_info:
            response_validator.validate(request, response)

        assert exc_info.value.__cause__ == MediaTypeDeserializeError(
            mimetype="application/json", value=b"abcde"
        )

    def test_invalid_media_type_value(self, response_validator):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"{}")

        with pytest.raises(DataValidationError) as exc_info:
            response_validator.validate(request, response)

        assert type(exc_info.value.__cause__) == InvalidSchemaValue

    def test_invalid_value(self, response_validator):
        request = MockRequest(self.host_url, "get", "/v1/tags")
        response_json = {
            "data": [
                {"id": 1, "name": "Sparky"},
            ],
        }
        response_data = json.dumps(response_json).encode()
        response = MockResponse(response_data)

        with pytest.raises(InvalidData) as exc_info:
            response_validator.validate(request, response)

        assert type(exc_info.value.__cause__) == InvalidSchemaValue

    def test_invalid_header(self, response_validator):
        request = MockRequest(
            self.host_url,
            "delete",
            "/v1/tags",
            path_pattern="/v1/tags",
        )
        response_json = {
            "data": [
                {
                    "id": 1,
                    "name": "Sparky",
                    "ears": {
                        "healthy": True,
                    },
                },
            ],
        }
        response_data = json.dumps(response_json).encode()
        headers = {
            "x-delete-confirm": "true",
            "x-delete-date": "today",
        }
        response = MockResponse(response_data, headers=headers)

        with pytest.raises(InvalidHeader):
            with pytest.warns(DeprecationWarning):
                response_validator.validate(request, response)

    def test_valid(self, response_validator):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response_json = {
            "data": [
                {
                    "id": 1,
                    "name": "Sparky",
                    "ears": {
                        "healthy": True,
                    },
                },
            ],
        }
        response_data = json.dumps(response_json).encode()
        response = MockResponse(response_data)

        result = response_validator.validate(request, response)

        assert result is None
