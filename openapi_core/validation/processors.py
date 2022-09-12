"""OpenAPI core validation processors module"""
from openapi_core.spec import Spec
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.response.protocols import ResponseValidator


class OpenAPIProcessor:
    def __init__(
        self,
        request_validator: RequestValidator,
        response_validator: ResponseValidator,
    ):
        self.request_validator = request_validator
        self.response_validator = response_validator

    def process_request(
        self, spec: Spec, request: Request
    ) -> RequestValidationResult:
        return self.request_validator.validate(spec, request)

    def process_response(
        self, spec: Spec, request: Request, response: Response
    ) -> ResponseValidationResult:
        return self.response_validator.validate(spec, request, response)
