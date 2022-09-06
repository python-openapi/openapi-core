"""OpenAPI core validation shortcuts module"""
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator


def validate_request(
    spec, request, base_url=None, validator=openapi_request_validator
):
    result = validator.validate(spec, request, base_url=base_url)
    result.raise_for_errors()
    return result


def validate_response(
    spec,
    request,
    response,
    base_url=None,
    validator=openapi_response_validator,
):
    result = validator.validate(spec, request, response, base_url=base_url)
    result.raise_for_errors()
    return result
