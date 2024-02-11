"""OpenAPI core unmarshalling processors module"""

from typing import Generic

from openapi_core.app import OpenAPI
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.typing import RequestType
from openapi_core.typing import ResponseType


class ValidationIntegration(Generic[RequestType, ResponseType]):
    def __init__(
        self,
        openapi: OpenAPI,
    ):
        self.openapi = openapi

    def get_openapi_request(self, request: RequestType) -> Request:
        raise NotImplementedError

    def get_openapi_response(self, response: ResponseType) -> Response:
        raise NotImplementedError

    def validate_request(self, request: RequestType) -> None:
        openapi_request = self.get_openapi_request(request)
        self.openapi.validate_request(
            openapi_request,
        )

    def validate_response(
        self,
        request: RequestType,
        response: ResponseType,
    ) -> None:
        openapi_request = self.get_openapi_request(request)
        openapi_response = self.get_openapi_response(response)
        self.openapi.validate_response(openapi_request, openapi_response)
