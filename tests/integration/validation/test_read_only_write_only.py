import json

import pytest

from openapi_core.spec import OpenAPIv30Spec as Spec
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator


@pytest.fixture(scope="class")
def spec(factory):
    spec_dict = factory.spec_from_file("data/v3.0/read_only_write_only.yaml")
    return Spec.create(spec_dict)


class TestReadOnly:
    def test_write_a_read_only_property(self, spec):
        data = json.dumps(
            {
                "id": 10,
                "name": "Pedro",
            }
        )

        request = MockRequest(
            host_url="", method="POST", path="/users", data=data
        )

        result = openapi_request_validator.validate(spec, request)

        assert type(result.errors[0]) == InvalidSchemaValue
        assert result.body is None

    def test_read_only_property_response(self, spec):
        data = json.dumps(
            {
                "id": 10,
                "name": "Pedro",
            }
        )

        request = MockRequest(host_url="", method="POST", path="/users")

        response = MockResponse(data)

        result = openapi_response_validator.validate(spec, request, response)

        assert not result.errors
        assert result.data == {
            "id": 10,
            "name": "Pedro",
        }


class TestWriteOnly:
    def test_write_only_property(self, spec):
        data = json.dumps(
            {
                "name": "Pedro",
                "hidden": False,
            }
        )

        request = MockRequest(
            host_url="", method="POST", path="/users", data=data
        )

        result = openapi_request_validator.validate(spec, request)

        assert not result.errors
        assert result.body == {
            "name": "Pedro",
            "hidden": False,
        }

    def test_read_a_write_only_property(self, spec):
        data = json.dumps(
            {
                "id": 10,
                "name": "Pedro",
                "hidden": True,
            }
        )

        request = MockRequest(host_url="", method="POST", path="/users")
        response = MockResponse(data)

        result = openapi_response_validator.validate(spec, request, response)

        assert type(result.errors[0]) == InvalidSchemaValue
        assert result.data is None
