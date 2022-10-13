import json
import uuid
from dataclasses import is_dataclass

import pytest

from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.validation.response import openapi_v30_response_validator


@pytest.fixture(scope="class")
def spec(factory):
    return factory.spec_from_file("data/v3.0/nullable_ref.yaml")


class TestNullableRefs:
    @pytest.mark.xfail(message="The nullable attribute should be respected")
    def test_with_null_value(self, spec):
        person = {
            "id": str(uuid.uuid4()),
            "name": "Joe Bloggs",
            "user": None,
        }
        request = MockRequest("", "get", f"/people/{person['id']}")
        response = MockResponse(json.dumps(person))

        result = openapi_v30_response_validator.validate(
            spec, request, response
        )

        assert not result.errors
        assert is_dataclass(result.data)
        assert result.data.__class__.__name__ == "Person"
        assert result.data.id == uuid.UUID(person["id"])
        assert result.data.name == person["name"]
        assert result.data.user is None

    def test_with_non_null_value(self, spec):
        person = {
            "id": str(uuid.uuid4()),
            "name": "Joe Bloggs",
            "user": {
                "id": str(uuid.uuid4()),
                "username": "joebloggs",
            },
        }
        request = MockRequest("", "get", f"/people/{person['id']}")
        response = MockResponse(json.dumps(person))

        result = openapi_v30_response_validator.validate(
            spec, request, response
        )

        assert not result.errors
        assert is_dataclass(result.data)
        assert result.data.__class__.__name__ == "Person"
        assert result.data.id == uuid.UUID(person["id"])
        assert result.data.name == person["name"]
        assert result.data.user is not None
        assert result.data.user.id == uuid.UUID(person["user"]["id"])
        assert result.data.user.username == person["user"]["username"]
