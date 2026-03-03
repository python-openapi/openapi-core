from typing import Optional
from typing import Type

from falcon.request import Request
from falcon.response import Response

from openapi_core import OpenAPI
from openapi_core.contrib.falcon.requests import FalconAsgiOpenAPIRequest
from openapi_core.contrib.falcon.requests import FalconOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconAsgiOpenAPIResponse
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponse
from openapi_core.unmarshalling.processors import AsyncUnmarshallingProcessor
from openapi_core.unmarshalling.processors import UnmarshallingProcessor
from openapi_core.unmarshalling.typing import ErrorsHandlerCallable


class FalconIntegration(UnmarshallingProcessor[Request, Response]):
    request_cls = FalconOpenAPIRequest
    response_cls = FalconOpenAPIResponse

    def get_openapi_request(self, request: Request) -> FalconOpenAPIRequest:
        return self.request_cls(request)

    def get_openapi_response(
        self, response: Response
    ) -> FalconOpenAPIResponse:
        assert self.response_cls is not None
        return self.response_cls(response)

    def should_validate_response(self) -> bool:
        return self.response_cls is not None

    def handle_response(
        self,
        request: Request,
        response: Response,
        errors_handler: ErrorsHandlerCallable[Response],
    ) -> Response:
        if not self.should_validate_response():
            return response
        return super().handle_response(request, response, errors_handler)


class AsyncFalconIntegration(AsyncUnmarshallingProcessor[Request, Response]):
    request_cls: Type[FalconAsgiOpenAPIRequest] = FalconAsgiOpenAPIRequest
    response_cls: Optional[Type[FalconAsgiOpenAPIResponse]] = (
        FalconAsgiOpenAPIResponse
    )

    def __init__(
        self,
        openapi: OpenAPI,
        request_cls: Type[FalconAsgiOpenAPIRequest] = FalconAsgiOpenAPIRequest,
        response_cls: Optional[Type[FalconAsgiOpenAPIResponse]] = (
            FalconAsgiOpenAPIResponse
        ),
    ):
        super().__init__(openapi)
        self.request_cls = request_cls or self.request_cls
        self.response_cls = response_cls

    async def get_openapi_request(
        self, request: Request
    ) -> FalconAsgiOpenAPIRequest:
        return await self.request_cls.from_request(request)

    async def get_openapi_response(
        self, response: Response
    ) -> FalconAsgiOpenAPIResponse:
        assert self.response_cls is not None
        return await self.response_cls.from_response(response)

    def should_validate_response(self) -> bool:
        return self.response_cls is not None

    async def handle_response(
        self,
        request: Request,
        response: Response,
        errors_handler: ErrorsHandlerCallable[Response],
    ) -> Response:
        if not self.should_validate_response():
            return response
        return await super().handle_response(request, response, errors_handler)
