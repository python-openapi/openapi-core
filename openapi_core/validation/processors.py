"""OpenAPI core validation processors module"""
from typing import Any
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.typing import RequestType
from openapi_core.typing import ResponseType
from openapi_core.validation.integrations import ValidationIntegration
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.response.types import ResponseValidatorType


class ValidationProcessor(ValidationIntegration[RequestType, ResponseType]):
    def handle_request(self, request: RequestType) -> None:
        self.validate_request(request)

    def handle_response(
        self, request: RequestType, response: ResponseType
    ) -> None:
        self.validate_response(request, response)
