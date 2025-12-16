"""OpenAPI core contrib starlette middlewares module"""

from typing import Type

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from openapi_core import OpenAPI
from openapi_core.contrib.starlette.handlers import (
    StarletteOpenAPIErrorsHandler,
)
from openapi_core.contrib.starlette.handlers import (
    StarletteOpenAPIValidRequestHandler,
)
from openapi_core.contrib.starlette.integrations import StarletteIntegration
from openapi_core.contrib.starlette.requests import StarletteOpenAPIRequest
from openapi_core.contrib.starlette.responses import StarletteOpenAPIResponse


class StarletteOpenAPIMiddleware(StarletteIntegration, BaseHTTPMiddleware):
    valid_request_handler_cls = StarletteOpenAPIValidRequestHandler
    errors_handler = StarletteOpenAPIErrorsHandler()

    def __init__(
        self,
        app: ASGIApp,
        openapi: OpenAPI,
        request_cls: Type[StarletteOpenAPIRequest] = StarletteOpenAPIRequest,
        response_cls: Type[
            StarletteOpenAPIResponse
        ] = StarletteOpenAPIResponse,
    ):
        super().__init__(openapi)
        self.request_cls = request_cls
        self.response_cls = response_cls
        BaseHTTPMiddleware.__init__(self, app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        valid_request_handler = self.valid_request_handler_cls(
            request, call_next
        )
        response = await self.handle_request(
            request, valid_request_handler, self.errors_handler
        )
        return await self.handle_response(
            request, response, self.errors_handler
        )
