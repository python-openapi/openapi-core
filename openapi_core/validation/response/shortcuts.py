"""OpenAPI core validation response shortcuts module"""
from openapi_core.validation.response.validators import ResponseDataValidator
from openapi_core.validation.response.validators import (
    ResponseHeadersValidator,
)
from openapi_core.validation.response.validators import ResponseValidator


def validate_response(validator, request, response):
    result = validator.validate(request, response)
    result.raise_for_errors()
    return result


def spec_validate_response(spec, request, response, base_url=None):
    validator = ResponseValidator(
        spec,
        base_url=base_url,
        custom_formatters=None,
        custom_media_type_deserializers=None,
    )
    return validate_response(validator, request, response)


def spec_validate_data(spec, request, response, base_url=None):
    validator = ResponseDataValidator(
        spec,
        base_url=base_url,
    )
    result = validate_response(validator, request, response)
    return result.data


def spec_validate_headers(spec, request, response, base_url=None):
    validator = ResponseHeadersValidator(
        spec,
        base_url=base_url,
    )
    result = validate_response(validator, request, response)
    return result.headers
