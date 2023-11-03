"""OpenAPI core contrib starlette middlewares module"""
from typing import Callable

from aioitertools.builtins import list as alist
from aioitertools.itertools import tee as atee
from jsonschema_path import SchemaPath
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.responses import StreamingResponse
from starlette.types import ASGIApp

from openapi_core.contrib.starlette.handlers import (
    StarletteOpenAPIErrorsHandler,
)
from openapi_core.contrib.starlette.handlers import (
    StarletteOpenAPIValidRequestHandler,
)
from openapi_core.contrib.starlette.requests import StarletteOpenAPIRequest
from openapi_core.contrib.starlette.responses import StarletteOpenAPIResponse
from openapi_core.unmarshalling.processors import AsyncUnmarshallingProcessor


class StarletteOpenAPIMiddleware(
    BaseHTTPMiddleware, AsyncUnmarshallingProcessor[Request, Response]
):
    request_cls = StarletteOpenAPIRequest
    response_cls = StarletteOpenAPIResponse
    valid_request_handler_cls = StarletteOpenAPIValidRequestHandler
    errors_handler = StarletteOpenAPIErrorsHandler()

    def __init__(self, app: ASGIApp, spec: SchemaPath):
        BaseHTTPMiddleware.__init__(self, app)
        AsyncUnmarshallingProcessor.__init__(self, spec)

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

    async def _get_openapi_request(
        self, request: Request
    ) -> StarletteOpenAPIRequest:
        body = await request.body()
        return self.request_cls(request, body)

    async def _get_openapi_response(
        self, response: Response
    ) -> StarletteOpenAPIResponse:
        assert self.response_cls is not None
        data = None
        if isinstance(response, StreamingResponse):
            body_iter1, body_iter2 = atee(response.body_iterator)
            response.body_iterator = body_iter2
            data = b"".join(
                [
                    chunk.encode(response.charset)
                    if not isinstance(chunk, bytes)
                    else chunk
                    async for chunk in body_iter1
                ]
            )
        return self.response_cls(response, data=data)

    def _validate_response(self) -> bool:
        return self.response_cls is not None
