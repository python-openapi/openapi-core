"""OpenAPI core unmarshalling processors module"""

from typing import Generic

from openapi_core.app import OpenAPI
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.typing import RequestType
from openapi_core.typing import ResponseType
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.validation.integrations import ValidationIntegration


class UnmarshallingIntegration(
    ValidationIntegration[RequestType, ResponseType]
):
    def unmarshal_request(
        self, request: RequestType
    ) -> RequestUnmarshalResult:
        openapi_request = self.get_openapi_request(request)
        return self.openapi.unmarshal_request(
            openapi_request,
        )

    def unmarshal_response(
        self,
        request: RequestType,
        response: ResponseType,
    ) -> ResponseUnmarshalResult:
        openapi_request = self.get_openapi_request(request)
        openapi_response = self.get_openapi_response(response)
        return self.openapi.unmarshal_response(
            openapi_request, openapi_response
        )


class AsyncUnmarshallingIntegration(Generic[RequestType, ResponseType]):
    def __init__(
        self,
        openapi: OpenAPI,
    ):
        self.openapi = openapi

    async def get_openapi_request(self, request: RequestType) -> Request:
        raise NotImplementedError

    async def get_openapi_response(self, response: ResponseType) -> Response:
        raise NotImplementedError

    async def unmarshal_request(
        self,
        request: RequestType,
    ) -> RequestUnmarshalResult:
        openapi_request = await self.get_openapi_request(request)
        return self.openapi.unmarshal_request(openapi_request)

    async def unmarshal_response(
        self,
        request: RequestType,
        response: ResponseType,
    ) -> ResponseUnmarshalResult:
        openapi_request = await self.get_openapi_request(request)
        openapi_response = await self.get_openapi_response(response)
        return self.openapi.unmarshal_response(
            openapi_request, openapi_response
        )
