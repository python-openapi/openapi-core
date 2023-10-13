from dataclasses import is_dataclass

import pytest
from jsonschema_path import SchemaPath

from openapi_core import V30RequestUnmarshaller
from openapi_core import unmarshal_request
from openapi_core import validate_request
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.datatypes import Parameters
from openapi_core.testing import MockRequest
from openapi_core.validation.request.exceptions import MissingRequiredParameter
from openapi_core.validation.request.exceptions import ParameterValidationError


class TestPathItemParamsValidator:
    @pytest.fixture(scope="session")
    def spec_dict(self):
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test path item parameter validation",
                "version": "0.1",
            },
            "paths": {
                "/resource": {
                    "parameters": [
                        {
                            "name": "resId",
                            "in": "query",
                            "required": True,
                            "schema": {
                                "type": "integer",
                            },
                        },
                    ],
                    "get": {
                        "responses": {
                            "default": {"description": "Return the resource."}
                        }
                    },
                }
            },
        }

    @pytest.fixture(scope="session")
    def spec(self, spec_dict):
        return SchemaPath.from_dict(spec_dict)

    @pytest.fixture(scope="session")
    def request_unmarshaller(self, spec):
        return V30RequestUnmarshaller(spec)

    def test_request_missing_param(self, request_unmarshaller):
        request = MockRequest("http://example.com", "get", "/resource")

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == Parameters()

    def test_request_invalid_param(self, request_unmarshaller):
        request = MockRequest(
            "http://example.com",
            "get",
            "/resource",
            args={"resId": "invalid"},
        )

        result = request_unmarshaller.unmarshal(request)

        assert result.errors == [
            ParameterValidationError(name="resId", location="query")
        ]
        assert type(result.errors[0].__cause__) is CastError
        assert result.body is None
        assert result.parameters == Parameters()

    def test_request_valid_param(self, request_unmarshaller):
        request = MockRequest(
            "http://example.com",
            "get",
            "/resource",
            args={"resId": "10"},
        )

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 0
        assert result.body is None
        assert result.parameters == Parameters(query={"resId": 10})

    def test_request_override_param(self, spec, spec_dict):
        # override path parameter on operation
        spec_dict["paths"]["/resource"]["get"]["parameters"] = [
            {
                # full valid parameter object required
                "name": "resId",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "integer",
                },
            }
        ]
        request = MockRequest("http://example.com", "get", "/resource")
        result = unmarshal_request(
            request, spec, base_url="http://example.com"
        )

        assert len(result.errors) == 0
        assert result.body is None
        assert result.parameters == Parameters()

    def test_request_override_param_uniqueness(self, spec, spec_dict):
        # add parameter on operation with same name as on path but
        # different location
        spec_dict["paths"]["/resource"]["get"]["parameters"] = [
            {
                # full valid parameter object required
                "name": "resId",
                "in": "header",
                "required": False,
                "schema": {
                    "type": "integer",
                },
            }
        ]
        request = MockRequest("http://example.com", "get", "/resource")
        with pytest.raises(MissingRequiredParameter):
            validate_request(request, spec, base_url="http://example.com")

    def test_request_object_deep_object_params(self, spec, spec_dict):
        # override path parameter on operation
        spec_dict["paths"]["/resource"]["parameters"] = [
            {
                # full valid parameter object required
                "name": "paramObj",
                "in": "query",
                "required": True,
                "schema": {
                    "x-model": "paramObj",
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                },
                "explode": True,
                "style": "deepObject",
            }
        ]

        request = MockRequest(
            "http://example.com",
            "get",
            "/resource",
            args={"paramObj[count]": 2, "paramObj[name]": "John"},
        )
        result = unmarshal_request(
            request, spec, base_url="http://example.com"
        )

        assert len(result.errors) == 0
        assert result.body is None
        assert len(result.parameters.query) == 1
        assert is_dataclass(result.parameters.query["paramObj"])
        assert result.parameters.query["paramObj"].count == 2
        assert result.parameters.query["paramObj"].name == "John"
