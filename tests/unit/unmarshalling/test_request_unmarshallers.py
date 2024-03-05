import enum

import pytest
from jsonschema_path import SchemaPath

from openapi_core import V30RequestUnmarshaller
from openapi_core import V31RequestUnmarshaller
from openapi_core.datatypes import Parameters
from openapi_core.testing import MockRequest


class Colors(enum.Enum):

    YELLOW = "yellow"
    BLUE = "blue"
    RED = "red"

    @classmethod
    def of(cls, v: str):
        for it in cls:
            if it.value == v:
                return it
        raise ValueError(f"Invalid value: {v}")


class TestRequestUnmarshaller:

    @pytest.fixture(scope="session")
    def spec_dict(self):
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Test request body unmarshaller",
                "version": "0.1",
            },
            "paths": {
                "/resources": {
                    "post": {
                        "description": "POST resources test request",
                        "requestBody": {
                            "description": "",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/createResource"
                                    }
                                }
                            },
                        },
                        "responses": {
                            "201": {"description": "Resource was created."}
                        },
                    },
                    "get": {
                        "description": "POST resources test request",
                        "parameters": [
                            {
                                "name": "color",
                                "in": "query",
                                "required": False,
                                "schema": {
                                    "$ref": "#/components/schemas/colors"
                                },
                            },
                        ],
                        "responses": {
                            "default": {
                                "description": "Returned resources matching request."
                            }
                        },
                    },
                }
            },
            "components": {
                "schemas": {
                    "colors": {
                        "type": "string",
                        "enum": ["yellow", "blue", "red"],
                        "format": "enum_Colors",
                    },
                    "createResource": {
                        "type": "object",
                        "properties": {
                            "resId": {"type": "integer"},
                            "color": {"$ref": "#/components/schemas/colors"},
                        },
                        "required": ["resId", "color"],
                    },
                }
            },
        }

    @pytest.fixture(scope="session")
    def spec(self, spec_dict):
        return SchemaPath.from_dict(spec_dict)

    @pytest.mark.parametrize(
        "req_unmarshaller_cls",
        [V30RequestUnmarshaller, V31RequestUnmarshaller],
    )
    def test_request_body_extra_unmarshaller(self, spec, req_unmarshaller_cls):
        ru = req_unmarshaller_cls(
            spec=spec, extra_format_unmarshallers={"enum_Colors": Colors.of}
        )
        request = MockRequest(
            host_url="http://example.com",
            method="post",
            path="/resources",
            data=b'{"resId": 23498572, "color": "blue"}',
        )
        result = ru.unmarshal(request)

        assert not result.errors
        assert result.body == {"resId": 23498572, "color": Colors.BLUE}
        assert result.parameters == Parameters()

    @pytest.mark.parametrize(
        "req_unmarshaller_cls",
        [V30RequestUnmarshaller, V31RequestUnmarshaller],
    )
    def test_request_param_extra_unmarshaller(
        self, spec, req_unmarshaller_cls
    ):
        ru = req_unmarshaller_cls(
            spec=spec, extra_format_unmarshallers={"enum_Colors": Colors.of}
        )
        request = MockRequest(
            host_url="http://example.com",
            method="get",
            path="/resources",
            args={"color": "blue"},
        )
        result = ru.unmarshal(request)

        assert not result.errors
        assert result.parameters == Parameters(query=dict(color=Colors.BLUE))
