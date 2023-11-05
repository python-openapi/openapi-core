import json
from dataclasses import is_dataclass

import pytest

from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.unmarshalling.request.unmarshallers import (
    V30RequestUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V30ResponseUnmarshaller,
)
from openapi_core.validation.request.exceptions import InvalidRequestBody
from openapi_core.validation.response.exceptions import InvalidData


@pytest.fixture(scope="class")
def schema_path(schema_path_factory):
    return schema_path_factory.from_file("data/v3.0/read_only_write_only.yaml")


@pytest.fixture(scope="class")
def request_unmarshaller(schema_path):
    return V30RequestUnmarshaller(schema_path)


@pytest.fixture(scope="class")
def response_unmarshaller(schema_path):
    return V30ResponseUnmarshaller(schema_path)


class TestReadOnly:
    def test_write_a_read_only_property(self, request_unmarshaller):
        data = json.dumps(
            {
                "id": 10,
                "name": "Pedro",
            }
        ).encode()

        request = MockRequest(
            host_url="", method="POST", path="/users", data=data
        )

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidRequestBody
        assert result.body is None

    def test_read_only_property_response(self, response_unmarshaller):
        data = json.dumps(
            {
                "id": 10,
                "name": "Pedro",
            }
        ).encode()

        request = MockRequest(host_url="", method="POST", path="/users")

        response = MockResponse(data)

        result = response_unmarshaller.unmarshal(request, response)

        assert not result.errors
        assert is_dataclass(result.data)
        assert result.data.__class__.__name__ == "User"
        assert result.data.id == 10
        assert result.data.name == "Pedro"


class TestWriteOnly:
    def test_write_only_property(self, request_unmarshaller):
        data = json.dumps(
            {
                "name": "Pedro",
                "hidden": False,
            }
        ).encode()

        request = MockRequest(
            host_url="", method="POST", path="/users", data=data
        )

        result = request_unmarshaller.unmarshal(request)

        assert not result.errors
        assert is_dataclass(result.body)
        assert result.body.__class__.__name__ == "User"
        assert result.body.name == "Pedro"
        assert result.body.hidden == False

    def test_read_a_write_only_property(self, response_unmarshaller):
        data = json.dumps(
            {
                "id": 10,
                "name": "Pedro",
                "hidden": True,
            }
        ).encode()

        request = MockRequest(host_url="", method="POST", path="/users")
        response = MockResponse(data)

        result = response_unmarshaller.unmarshal(request, response)

        assert result.errors == [InvalidData()]
        assert result.data is None
