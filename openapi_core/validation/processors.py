"""OpenAPI core validation processors module"""

from openapi_core.typing import RequestType
from openapi_core.typing import ResponseType
from openapi_core.validation.integrations import ValidationIntegration


class ValidationProcessor(ValidationIntegration[RequestType, ResponseType]):
    def handle_request(self, request: RequestType) -> None:
        self.validate_request(request)

    def handle_response(
        self, request: RequestType, response: ResponseType
    ) -> None:
        self.validate_response(request, response)
