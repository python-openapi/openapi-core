from typing import Optional

import pytest

from openapi_core import OpenAPI
from openapi_core.deserializing.styles.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.testing import MockRequest
from openapi_core.validation.request.exceptions import InvalidParameter
from openapi_core.validation.request.exceptions import ParameterValidationError
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue

OPENAPI_VERSIONS = ["3.0.4", "3.1.1", "3.2.0"]


def make_openapi(openapi_version, schema, **parameter_options):
    return OpenAPI.from_dict(
        {
            "openapi": openapi_version,
            "info": {"title": "Empty query parameter", "version": "1.0.0"},
            "paths": {
                "/api": {
                    "get": {
                        "parameters": [
                            {
                                "name": "status",
                                "in": "query",
                                "schema": schema,
                                **parameter_options,
                            }
                        ],
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        }
    )


def make_request(value: Optional[str] = ""):
    args = {} if value is None else {"status": value}
    return MockRequest("http://localhost", "get", "/api", args=args)


@pytest.mark.parametrize("openapi_version", OPENAPI_VERSIONS)
@pytest.mark.parametrize(
    "schema", [{"enum": ["Active", ""]}, {"type": "string"}]
)
def test_empty_query_parameter_allowed_by_schema(openapi_version, schema):
    openapi = make_openapi(openapi_version, schema)
    request = make_request()

    assert list(openapi.iter_request_errors(request)) == []
    result = openapi.unmarshal_request(request)
    assert result.errors == []
    assert result.parameters.query == {"status": ""}


@pytest.mark.parametrize("openapi_version", OPENAPI_VERSIONS)
@pytest.mark.parametrize(
    "schema", [{"enum": ["Active"]}, {"type": "string", "minLength": 1}]
)
def test_empty_query_parameter_rejected_by_schema(openapi_version, schema):
    openapi = make_openapi(openapi_version, schema)
    request = make_request()

    validation_errors = list(openapi.iter_request_errors(request))
    assert len(validation_errors) == 1
    assert type(validation_errors[0]) is InvalidParameter
    assert type(validation_errors[0].__cause__) is InvalidSchemaValue

    result = openapi.unmarshal_request(request)
    errors = list(result.errors)
    assert len(errors) == 1
    assert type(errors[0]) is InvalidParameter
    assert type(errors[0].__cause__) is InvalidSchemaValue


@pytest.mark.parametrize("openapi_version", OPENAPI_VERSIONS)
def test_allow_empty_value_false_preserves_legacy_error(openapi_version):
    openapi = make_openapi(
        openapi_version, {"enum": ["Active", ""]}, allowEmptyValue=False
    )
    request = make_request()

    with pytest.warns(DeprecationWarning, match="allowEmptyValue"):
        validation_errors = list(openapi.iter_request_errors(request))
    assert len(validation_errors) == 1
    assert type(validation_errors[0]) is ParameterValidationError
    assert type(validation_errors[0].__cause__) is EmptyQueryParameterValue

    with pytest.warns(DeprecationWarning, match="allowEmptyValue"):
        result = openapi.unmarshal_request(request)
    errors = list(result.errors)
    assert len(errors) == 1
    assert type(errors[0]) is ParameterValidationError
    assert type(errors[0].__cause__) is EmptyQueryParameterValue


@pytest.mark.parametrize("openapi_version", OPENAPI_VERSIONS)
def test_missing_query_parameter_remains_omitted(openapi_version):
    openapi = make_openapi(openapi_version, {"type": "string"})
    request = make_request(None)

    assert list(openapi.iter_request_errors(request)) == []
    result = openapi.unmarshal_request(request)
    assert result.errors == []
    assert result.parameters.query == {}
