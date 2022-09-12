"""OpenAPI core validation shortcuts module"""
from typing import Optional

from openapi_core.spec import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.response import openapi_response_validator
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.response.protocols import ResponseValidator


def validate_request(
    spec: Spec,
    request: Request,
    base_url: Optional[str] = None,
    validator: RequestValidator = openapi_request_validator,
) -> RequestValidationResult:
    result = validator.validate(spec, request, base_url=base_url)
    result.raise_for_errors()
    return result


def validate_response(
    spec: Spec,
    request: Request,
    response: Response,
    base_url: Optional[str] = None,
    validator: ResponseValidator = openapi_response_validator,
) -> ResponseValidationResult:
    result = validator.validate(spec, request, response, base_url=base_url)
    result.raise_for_errors()
    return result
