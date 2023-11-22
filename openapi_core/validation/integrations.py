"""OpenAPI core unmarshalling processors module"""
from typing import Any
from typing import Generic
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.app import OpenAPI
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.typing import RequestType
from openapi_core.typing import ResponseType
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.processors import (
    RequestUnmarshallingProcessor,
)
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.processors import (
    ResponseUnmarshallingProcessor,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.typing import AsyncValidRequestHandlerCallable
from openapi_core.unmarshalling.typing import ErrorsHandlerCallable
from openapi_core.unmarshalling.typing import ValidRequestHandlerCallable


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
