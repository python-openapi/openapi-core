import json
from dataclasses import is_dataclass

import pytest

from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.responses.exceptions import ResponseNotFound
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.unmarshalling.response.unmarshallers import (
    V30ResponseUnmarshaller,
)
from openapi_core.validation.response.exceptions import DataValidationError
from openapi_core.validation.response.exceptions import InvalidData
from openapi_core.validation.response.exceptions import InvalidHeader
from openapi_core.validation.response.exceptions import MissingData
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue


class TestResponseUnmarshaller:
    host_url = "http://petstore.swagger.io"

    @pytest.fixture(scope="session")
    def spec_dict(self, v30_petstore_content):
        return v30_petstore_content

    @pytest.fixture(scope="session")
    def spec(self, v30_petstore_spec):
        return v30_petstore_spec

    @pytest.fixture(scope="session")
    def response_unmarshaller(self, spec):
        return V30ResponseUnmarshaller(spec)

    def test_invalid_server(self, response_unmarshaller):
        request = MockRequest("http://petstore.invalid.net/v1", "get", "/")
        response = MockResponse(b"Not Found", status_code=404)

        result = response_unmarshaller.unmarshal(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_operation(self, response_unmarshaller):
        request = MockRequest(self.host_url, "patch", "/v1/pets")
        response = MockResponse(b"Not Found", status_code=404)

        result = response_unmarshaller.unmarshal(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == OperationNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_response(self, response_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"Not Found", status_code=409)

        result = response_unmarshaller.unmarshal(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == ResponseNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_content_type(self, response_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"Not Found", content_type="text/csv")

        result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == [DataValidationError()]
        assert type(result.errors[0].__cause__) == MediaTypeNotFound
        assert result.data is None
        assert result.headers == {}

    def test_missing_body(self, response_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(None)

        result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == [MissingData()]
        assert result.data is None
        assert result.headers == {}

    def test_invalid_media_type(self, response_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"abcde")

        result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == [DataValidationError()]
        assert result.errors[0].__cause__ == MediaTypeDeserializeError(
            mimetype="application/json", value=b"abcde"
        )
        assert result.data is None
        assert result.headers == {}

    def test_invalid_media_type_value(self, response_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(b"{}")

        result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == [InvalidData()]
        assert type(result.errors[0].__cause__) == InvalidSchemaValue
        assert result.data is None
        assert result.headers == {}

    def test_invalid_value(self, response_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1/tags")
        response_json = {
            "data": [
                {"id": 1, "name": "Sparky"},
            ],
        }
        response_data = json.dumps(response_json)
        response = MockResponse(response_data)

        result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == [InvalidData()]
        assert type(result.errors[0].__cause__) == InvalidSchemaValue
        assert result.data is None
        assert result.headers == {}

    def test_invalid_header(self, response_unmarshaller):
        userdata = {
            "name": 1,
        }
        userdata_json = json.dumps(userdata)
        cookies = {
            "user": "123",
            "userdata": userdata_json,
        }
        request = MockRequest(
            self.host_url,
            "delete",
            "/v1/tags",
            path_pattern="/v1/tags",
            cookies=cookies,
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

        with pytest.warns(DeprecationWarning):
            result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == [InvalidHeader(name="x-delete-date")]
        assert result.data is None
        assert result.headers == {"x-delete-confirm": True}

    def test_get_pets(self, response_unmarshaller):
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

        result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == []
        assert is_dataclass(result.data)
        assert len(result.data.data) == 1
        assert result.data.data[0].id == 1
        assert result.data.data[0].name == "Sparky"
        assert result.headers == {}
