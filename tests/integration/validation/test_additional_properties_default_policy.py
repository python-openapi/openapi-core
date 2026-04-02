import json

import pytest

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.validation.request.exceptions import InvalidRequestBody
from openapi_core.validation.response.exceptions import InvalidData


def _spec_dict():
    return {
        "openapi": "3.0.3",
        "info": {"title": "Strict additionalProperties", "version": "1.0.0"},
        "servers": [{"url": "http://example.com"}],
        "paths": {
            "/tags": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Tag"}
                            }
                        },
                    },
                    "responses": {"204": {"description": "No content"}},
                },
                "get": {
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Tag"
                                    }
                                }
                            },
                        }
                    }
                },
            }
        },
        "components": {
            "schemas": {
                "Tag": {
                    "type": "object",
                    "properties": {
                        "tag_name": {
                            "type": "string",
                        }
                    },
                    "required": ["tag_name"],
                }
            }
        },
    }


def test_request_validation_default_allows_extra_properties():
    openapi = OpenAPI.from_dict(_spec_dict())
    request = MockRequest(
        "http://example.com",
        "post",
        "/tags",
        content_type="application/json",
        data=json.dumps(
            {
                "tag_name": "my-tag",
                "sneaky_property": "sneaky data",
            }
        ).encode("utf-8"),
    )

    openapi.validate_request(request)


def test_request_validation_strict_rejects_extra_properties():
    config = Config(additional_properties_default_policy="forbid")
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest(
        "http://example.com",
        "post",
        "/tags",
        content_type="application/json",
        data=json.dumps(
            {
                "tag_name": "my-tag",
                "sneaky_property": "sneaky data",
            }
        ).encode("utf-8"),
    )

    with pytest.raises(InvalidRequestBody):
        openapi.validate_request(request)


def test_response_validation_default_allows_extra_properties():
    openapi = OpenAPI.from_dict(_spec_dict())
    request = MockRequest("http://example.com", "get", "/tags")
    response = MockResponse(
        data=json.dumps(
            {
                "tag_name": "my-tag",
                "sneaky_property": "sneaky data",
            }
        ).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    openapi.validate_response(request, response)


def test_response_validation_strict_rejects_extra_properties():
    config = Config(additional_properties_default_policy="forbid")
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest("http://example.com", "get", "/tags")
    response = MockResponse(
        data=json.dumps(
            {
                "tag_name": "my-tag",
                "sneaky_property": "sneaky data",
            }
        ).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    with pytest.raises(InvalidData):
        openapi.validate_response(request, response)


def test_request_validation_strict_error_message_is_stable():
    """Test that error messages are deterministic when multiple extra properties exist."""
    config = Config(additional_properties_default_policy="forbid")
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)

    request = MockRequest(
        "http://example.com",
        "post",
        "/tags",
        content_type="application/json",
        data=json.dumps(
            {
                "tag_name": "my-tag",
                "zebra": "z data",
                "apple": "a data",
                "mango": "m data",
            }
        ).encode("utf-8"),
    )

    # Collect error messages from multiple validation attempts
    messages = []
    for _ in range(10):
        with pytest.raises(InvalidRequestBody) as exc_info:
            openapi.validate_request(request)
        messages.append(str(exc_info.value))

    assert (
        len(set(messages)) == 1
    ), f"Error messages are not stable: {messages}"

    error_message = messages[0]
    assert (
        "'apple', 'mango', 'zebra'" in error_message
    ), f"Properties not in alphabetical order: {error_message}"


def test_response_validation_strict_allows_explicit_additional_properties_true():
    spec_dict = _spec_dict()
    spec_dict["components"]["schemas"]["Tag"]["additionalProperties"] = True

    config = Config(additional_properties_default_policy="forbid")
    openapi = OpenAPI.from_dict(spec_dict, config=config)
    request = MockRequest("http://example.com", "get", "/tags")
    response = MockResponse(
        data=json.dumps(
            {
                "tag_name": "my-tag",
                "sneaky_property": "sneaky data",
            }
        ).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    openapi.validate_response(request, response)
