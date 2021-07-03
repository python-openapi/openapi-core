"""OpenAPI core validation request shortcuts module"""
from functools import partial

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


def spec_validate_request(
    spec,
    request,
    request_factory=None,
    validator_class=RequestValidator,
    result_attribute=None,
):
    if request_factory is not None:
        request = request_factory(request)

    validator = validator_class(spec)

    result = validator.validate(request)
    result.raise_for_errors()

    if result_attribute is None:
        return result
    return getattr(result, result_attribute)


spec_validate_parameters = partial(
    spec_validate_request,
    validator_class=RequestParametersValidator,
    result_attribute="parameters",
)


spec_validate_body = partial(
    spec_validate_request,
    validator_class=RequestBodyValidator,
    result_attribute="body",
)


spec_validate_security = partial(
    spec_validate_request,
    validator_class=RequestSecurityValidator,
    result_attribute="security",
)
