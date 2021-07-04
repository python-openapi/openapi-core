"""OpenAPI core validation response shortcuts module"""
from functools import partial

from openapi_core.validation.response.validators import ResponseDataValidator
from openapi_core.validation.response.validators import (
    ResponseHeadersValidator,
)
from openapi_core.validation.response.validators import ResponseValidator


def validate_response(validator, request, response):
    result = validator.validate(request, response)
    result.raise_for_errors()
    return result


def spec_validate_response(
    spec,
    request,
    response,
    request_factory=None,
    response_factory=None,
    validator_class=ResponseValidator,
    result_attribute=None,
):
    if request_factory is not None:
        request = request_factory(request)
    if response_factory is not None:
        response = response_factory(response)

    validator = validator_class(spec)

    result = validator.validate(request, response)
    result.raise_for_errors()

    if result_attribute is None:
        return result
    return getattr(result, result_attribute)


spec_validate_data = partial(
    spec_validate_response,
    validator_class=ResponseDataValidator,
    result_attribute="data",
)


spec_validate_headers = partial(
    spec_validate_response,
    validator_class=ResponseHeadersValidator,
    result_attribute="headers",
)
