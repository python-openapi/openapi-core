"""OpenAPI core validation request shortcuts module"""
from functools import partial

from openapi_core.schema.media_types.exceptions import OpenAPIMediaTypeError
from openapi_core.schema.parameters.exceptions import OpenAPIParameterError
from openapi_core.schema.request_bodies.exceptions import (
    OpenAPIRequestBodyError,
)
from openapi_core.schema.schemas.exceptions import OpenAPISchemaError
from openapi_core.validation.request.validators import RequestValidator

ERRORS_BODY = (
    OpenAPIRequestBodyError, OpenAPIMediaTypeError, OpenAPISchemaError,
)
ERRORS_PARAMETERS = (
    OpenAPIParameterError,
)


def validate_request(validator, request, failsafe=None):
    if failsafe is None:
        failsafe = ()
    result = validator.validate(request)
    try:
        result.raise_for_errors()
    except failsafe:
        pass
    return result


validate_parameters = partial(validate_request, failsafe=ERRORS_BODY)
validate_body = partial(validate_request, failsafe=ERRORS_PARAMETERS)


def spec_validate_parameters(spec, request, request_factory=None):
    if request_factory is not None:
        request = request_factory(request)

    validator = RequestValidator(spec)
    result = validate_parameters(validator, request)

    return result.parameters


def spec_validate_body(spec, request, request_factory=None):
    if request_factory is not None:
        request = request_factory(request)

    validator = RequestValidator(spec)
    result = validate_body(validator, request)

    return result.body
