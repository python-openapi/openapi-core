"""OpenAPI core validation processors module"""
from typing import Any
from typing import Optional

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.shortcuts import get_classes
from openapi_core.spec import Spec
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.response.types import ResponseValidatorType


class ValidationProcessor:
    def __init__(
        self,
        spec: Spec,
        request_validator_cls: Optional[RequestValidatorType] = None,
        response_validator_cls: Optional[ResponseValidatorType] = None,
        **unmarshaller_kwargs: Any,
    ):
        self.spec = spec
        if request_validator_cls is None or response_validator_cls is None:
            classes = get_classes(self.spec)
            if request_validator_cls is None:
                request_validator_cls = classes.request_validator_cls
            if response_validator_cls is None:
                response_validator_cls = classes.response_validator_cls
        self.request_validator = request_validator_cls(
            self.spec, **unmarshaller_kwargs
        )
        self.response_validator = response_validator_cls(
            self.spec, **unmarshaller_kwargs
        )

    def process_request(self, request: Request) -> None:
        self.request_validator.validate(request)

    def process_response(self, request: Request, response: Response) -> None:
        self.response_validator.validate(request, response)
