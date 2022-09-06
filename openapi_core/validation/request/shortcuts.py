"""OpenAPI core validation request shortcuts module"""
from openapi_core.validation.request.validators import RequestBodyValidator
from openapi_core.validation.request.validators import (
    RequestParametersValidator,
)
from openapi_core.validation.request.validators import RequestSecurityValidator
from openapi_core.validation.request.validators import RequestValidator


def validate_request(validator, request):
    result = validator.validate(request)
    result.raise_for_errors()
    return result


def spec_validate_request(spec, request, base_url=None):
    validator = RequestValidator(
        spec,
        base_url=base_url,
    )
    return validate_request(validator, request)


def spec_validate_body(spec, request, base_url=None):
    validator = RequestBodyValidator(
        spec,
        base_url=base_url,
    )
    result = validate_request(validator, request)
    return result.body


def spec_validate_parameters(spec, request, base_url=None):
    validator = RequestParametersValidator(
        spec,
        base_url=base_url,
    )
    result = validate_request(validator, request)
    return result.parameters


def spec_validate_security(spec, request, base_url=None):
    validator = RequestSecurityValidator(
        spec,
        base_url=base_url,
    )
    result = validate_request(validator, request)
    return result.security
