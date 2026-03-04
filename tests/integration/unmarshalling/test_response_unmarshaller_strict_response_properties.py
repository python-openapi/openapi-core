import json

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
                }
            }
        },
        "components": {
            "schemas": {
                "Resource": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
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


def test_response_unmarshal_default_allows_missing_optional_properties():
    openapi = OpenAPI.from_dict(_spec_dict())
    request = MockRequest("http://example.com", "get", "/resources")
    response = MockResponse(
        data=json.dumps({"id": 1}).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    result = openapi.unmarshal_response(request, response)

    assert result.errors == []


def test_response_unmarshal_strict_rejects_missing_documented_properties():
    config = Config(strict_response_properties=True)
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest("http://example.com", "get", "/resources")
    response = MockResponse(
        data=json.dumps({"id": 1}).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    result = openapi.unmarshal_response(request, response)

    assert result.errors == [InvalidData()]
    assert result.data is None


def test_response_unmarshal_strict_excludes_write_only_properties():
    config = Config(strict_response_properties=True)
    openapi = OpenAPI.from_dict(_spec_dict(), config=config)
    request = MockRequest("http://example.com", "get", "/resources")
    response = MockResponse(
        data=json.dumps(
            {
                "id": 1,
                "name": "resource",
            }
        ).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    result = openapi.unmarshal_response(request, response)

    assert result.errors == []
