"""OpenAPI core validation processors module"""
from typing import Optional
from typing import Type

from openapi_core.spec import Spec
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.request.proxies import SpecRequestValidatorProxy
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.response.protocols import ResponseValidator
from openapi_core.validation.response.proxies import SpecResponseValidatorProxy
from openapi_core.validation.shortcuts import get_validators
from openapi_core.validation.shortcuts import validate_request
from openapi_core.validation.shortcuts import validate_response


class OpenAPISpecProcessor:
    def __init__(
        self,
        request_validator: SpecRequestValidatorProxy,
        response_validator: SpecResponseValidatorProxy,
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


class OpenAPIProcessor:
    def __init__(
        self,
        spec: Spec,
        request_validator_cls: Optional[Type[RequestValidator]] = None,
        response_validator_cls: Optional[Type[ResponseValidator]] = None,
    ):
        self.spec = spec
        if request_validator_cls is None or response_validator_cls is None:
            validators = get_validators(self.spec)
            if request_validator_cls is None:
                request_validator_cls = validators.request_cls
            if response_validator_cls is None:
                response_validator_cls = validators.response_cls
        self.request_validator = request_validator_cls(self.spec)
        self.response_validator = response_validator_cls(self.spec)

    def process_request(self, request: Request) -> RequestValidationResult:
        return self.request_validator.validate(request)

    def process_response(
        self, request: Request, response: Response
    ) -> ResponseValidationResult:
        return self.response_validator.validate(request, response)
