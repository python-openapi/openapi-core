"""OpenAPI core validation processors module"""
from openapi_core.spec.paths import SpecPath
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest, RequestValidationResult,
)
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import (
    OpenAPIResponse, ResponseValidationResult,
)
from openapi_core.validation.response.validators import ResponseValidator


class OpenAPIProcessor:

    def __init__(
        self,
        request_validator: RequestValidator,
        response_validator: ResponseValidator,
    ):
        self.request_validator = request_validator
        self.response_validator = response_validator

    @classmethod
    def from_spec(
            cls,
            spec: SpecPath,
    ) -> 'OpenAPIProcessor':
        request_validator = RequestValidator(spec)
        response_validator = ResponseValidator(spec)
        return cls(
            request_validator=request_validator,
            response_validator=response_validator,
        )

    def process_openapi_request(
        self,
        request: OpenAPIRequest,
    ) -> RequestValidationResult:
        return self.request_validator.validate(request)

    def process_openapi_response(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> ResponseValidationResult:
        return self.response_validator.validate(request, response)
