import json

import pytest
from jsonschema_path import SchemaPath

from openapi_core import V30RequestValidator
from openapi_core import V30ResponseValidator
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.validation.request.exceptions import InvalidRequestBody
from openapi_core.validation.response.exceptions import InvalidData


def _spec_schema_path() -> SchemaPath:
    spec_dict = {
        "openapi": "3.0.3",
        "info": {"title": "Strict JSON Validation", "version": "1.0.0"},
        "servers": [{"url": "http://example.com"}],
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            },
                            "application/problem+json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            },
                        },
                    },
                    "responses": {
                        "204": {"description": "No content"},
                    },
                },
                "put": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                },
                                "encoding": {
                                    "age": {"contentType": "application/json"},
                                },
                            }
                        },
                    },
                    "responses": {
                        "204": {"description": "No content"},
                    },
                },
                "get": {
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                },
                                "application/problem+json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                },
                            },
                        }
                    }
                },
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "username": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                    "required": ["id", "username", "age"],
                }
            }
        },
    }
    return SchemaPath.from_dict(spec_dict)


@pytest.mark.parametrize(
    "content_type",
    [
        "application/json",
        "application/problem+json",
    ],
)
def test_response_validator_strict_json_types(content_type: str) -> None:
    spec = _spec_schema_path()
    validator = V30ResponseValidator(spec)

    request = MockRequest("http://example.com", "get", "/users")
    response_json = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "Test User",
        "age": "30",
    }
    response = MockResponse(
        json.dumps(response_json).encode("utf-8"),
        status_code=200,
        content_type=content_type,
    )

    with pytest.raises(InvalidData):
        validator.validate(request, response)


@pytest.mark.parametrize(
    "content_type",
    [
        "application/json",
        "application/problem+json",
    ],
)
def test_request_validator_strict_json_types(content_type: str) -> None:
    spec = _spec_schema_path()
    validator = V30RequestValidator(spec)

    request_json = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "Test User",
        "age": "30",
    }
    request = MockRequest(
        "http://example.com",
        "post",
        "/users",
        content_type=content_type,
        data=json.dumps(request_json).encode("utf-8"),
    )

    with pytest.raises(InvalidRequestBody):
        validator.validate(request)


def test_request_validator_urlencoded_json_part_strict() -> None:
    spec = _spec_schema_path()
    validator = V30RequestValidator(spec)

    # urlencoded field age is declared as application/json (via encoding)
    # and contains a JSON string "30" (invalid for integer schema)
    request = MockRequest(
        "http://example.com",
        "put",
        "/users",
        content_type="application/x-www-form-urlencoded",
        data=(
            b"id=123e4567-e89b-12d3-a456-426614174000&"
            b"username=Test+User&"
            b"age=%2230%22"
        ),
    )

    with pytest.raises(InvalidRequestBody):
        validator.validate(request)


def test_response_validator_strict_json_nested_types() -> None:
    """Test that nested JSON structures (arrays, objects) remain strict."""
    spec_dict = {
        "openapi": "3.0.3",
        "info": {"title": "Nested JSON Test", "version": "1.0.0"},
        "servers": [{"url": "http://example.com"}],
        "paths": {
            "/data": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ids": {
                                                "type": "array",
                                                "items": {"type": "integer"},
                                            },
                                            "metadata": {
                                                "type": "object",
                                                "properties": {
                                                    "count": {
                                                        "type": "integer"
                                                    }
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    }
                }
            }
        },
    }
    spec = SchemaPath.from_dict(spec_dict)
    validator = V30ResponseValidator(spec)

    request = MockRequest("http://example.com", "get", "/data")

    # Test nested array with string integers (should fail)
    response_json = {"ids": ["10", "20", "30"], "metadata": {"count": 5}}
    response = MockResponse(
        json.dumps(response_json).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )
    with pytest.raises(InvalidData):
        validator.validate(request, response)

    # Test nested object with string integer (should fail)
    response_json2 = {"ids": [10, 20, 30], "metadata": {"count": "5"}}
    response2 = MockResponse(
        json.dumps(response_json2).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )
    with pytest.raises(InvalidData):
        validator.validate(request, response2)
