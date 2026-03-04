import json

import pytest

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.validation.response.exceptions import InvalidData


def _spec_dict():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Strict response properties",
            "version": "1.0.0",
        },
        "servers": [{"url": "http://example.com"}],
        "paths": {
            "/resources": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Resource"
                                    }
                                }
                            },
                        }
                    }
                },
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Resource"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                        }
                    },
                },
            }
        },
        "components": {
            "schemas": {
                "Resource": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "description": {
                            "type": "string",
                            "nullable": True,
                        },
                        "secret": {
                            "type": "string",
                            "writeOnly": True,
                        },
                    },
                    "required": ["id"],
                }
            }
        },
    }


def test_response_validation_default_allows_missing_optional_properties():
    openapi = OpenAPI.from_dict(_spec_dict())
    request = MockRequest("http://example.com", "get", "/resources")
    response = MockResponse(
        data=json.dumps({"id": 1}).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    openapi.validate_response(request, response)


def test_response_validation_strict_rejects_missing_documented_properties():
    config = Config(response_properties_default_policy="required")
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest("http://example.com", "get", "/resources")
    response = MockResponse(
        data=json.dumps({"id": 1}).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    with pytest.raises(InvalidData):
        openapi.validate_response(request, response)


def test_response_validation_strict_allows_nullable_properties_when_present():
    config = Config(response_properties_default_policy="required")
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest("http://example.com", "get", "/resources")
    response = MockResponse(
        data=json.dumps(
            {
                "id": 1,
                "name": "resource",
                "description": None,
            }
        ).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    openapi.validate_response(request, response)


def test_response_validation_strict_excludes_write_only_properties():
    config = Config(response_properties_default_policy="required")
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest("http://example.com", "get", "/resources")
    response = MockResponse(
        data=json.dumps(
            {
                "id": 1,
                "name": "resource",
                "description": "description",
            }
        ).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    openapi.validate_response(request, response)


def test_request_validation_ignores_response_properties_default_policy_flag():
    config = Config(response_properties_default_policy="required")
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest(
        "http://example.com",
        "post",
        "/resources",
        content_type="application/json",
        data=json.dumps({"id": 1}).encode("utf-8"),
    )

    openapi.validate_request(request)
