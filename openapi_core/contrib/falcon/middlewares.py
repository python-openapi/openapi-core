"""OpenAPI core contrib falcon middlewares module"""

from typing import Any
from typing import Optional
from typing import Type
from typing import cast

from falcon.request import Request
from falcon.response import Response
from jsonschema_path import SchemaPath

from openapi_core import OpenAPI
from openapi_core.contrib.falcon.handlers import FalconOpenAPIErrorsHandler
from openapi_core.contrib.falcon.handlers import (
    FalconOpenAPIValidRequestHandler,
)
from openapi_core.contrib.falcon.integrations import AsyncFalconIntegration
from openapi_core.contrib.falcon.integrations import FalconIntegration
from openapi_core.contrib.falcon.requests import FalconAsgiOpenAPIRequest
from openapi_core.contrib.falcon.requests import FalconOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconAsgiOpenAPIResponse
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponse
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType

_DEFAULT_ASYNC = object()


class FalconWSGIOpenAPIMiddleware(FalconIntegration):
    """OpenAPI middleware for Falcon WSGI applications.

    This class wires Falcon's synchronous middleware hooks to the
    synchronous OpenAPI integration.
    """

    valid_request_handler_cls = FalconOpenAPIValidRequestHandler
    errors_handler_cls: Type[FalconOpenAPIErrorsHandler] = (
        FalconOpenAPIErrorsHandler
    )

    def __init__(
        self,
        openapi: OpenAPI,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **kwargs: Any,
    ):
        super().__init__(openapi)
        self.request_cls = request_cls or self.request_cls
        self.response_cls = response_cls or self.response_cls
        self.errors_handler_cls = errors_handler_cls or self.errors_handler_cls

    @classmethod
    def from_spec(
        cls,
        spec: SchemaPath,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **kwargs: Any,
    ) -> "FalconWSGIOpenAPIMiddleware":
        openapi = OpenAPI.build(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
        )
        return cls(
            openapi,
            request_cls=request_cls,
            response_cls=response_cls,
            errors_handler_cls=errors_handler_cls,
            **kwargs,
        )

    def process_request(self, req: Request, resp: Response) -> None:
        valid_handler = self.valid_request_handler_cls(req, resp)
        errors_handler = self.errors_handler_cls(req, resp)
        self.handle_request(req, valid_handler, errors_handler)

    def process_response(
        self, req: Request, resp: Response, resource: Any, req_succeeded: bool
    ) -> None:
        errors_handler = self.errors_handler_cls(req, resp)
        self.handle_response(req, resp, errors_handler)


class FalconASGIOpenAPIMiddleware(AsyncFalconIntegration):
    """OpenAPI middleware for Falcon ASGI applications.

    This class wires Falcon's asynchronous middleware hooks to the
    asynchronous OpenAPI integration.
    """

    valid_request_handler_cls = FalconOpenAPIValidRequestHandler
    errors_handler_cls: Type[FalconOpenAPIErrorsHandler] = (
        FalconOpenAPIErrorsHandler
    )

    def __init__(
        self,
        openapi: OpenAPI,
        request_cls: Type[FalconAsgiOpenAPIRequest] = FalconAsgiOpenAPIRequest,
        response_cls: Optional[Type[FalconAsgiOpenAPIResponse]] = (
            FalconAsgiOpenAPIResponse
        ),
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **kwargs: Any,
    ):
        super().__init__(
            openapi,
            request_cls=request_cls,
            response_cls=response_cls,
        )
        self.errors_handler_cls = errors_handler_cls or self.errors_handler_cls

    @classmethod
    def from_spec(
        cls,
        spec: SchemaPath,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_cls: Type[FalconAsgiOpenAPIRequest] = FalconAsgiOpenAPIRequest,
        response_cls: Optional[Type[FalconAsgiOpenAPIResponse]] = (
            FalconAsgiOpenAPIResponse
        ),
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **kwargs: Any,
    ) -> "FalconASGIOpenAPIMiddleware":
        openapi = OpenAPI.build(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
        )
        return cls(
            openapi,
            request_cls=request_cls,
            response_cls=response_cls,
            errors_handler_cls=errors_handler_cls,
            **kwargs,
        )

    async def process_request_async(
        self, req: Request, resp: Response
    ) -> None:
        errors_handler = self.errors_handler_cls(req, resp)
        valid_request_handler = self.valid_request_handler_cls(req, resp)

        async def async_valid_request_handler(
            request_unmarshal_result: RequestUnmarshalResult,
        ) -> Response:
            return valid_request_handler(request_unmarshal_result)

        await self.handle_request(
            req,
            async_valid_request_handler,
            errors_handler,
        )

    async def process_response_async(
        self,
        req: Request,
        resp: Response,
        resource: Any,
        req_succeeded: bool,
    ) -> None:
        errors_handler = self.errors_handler_cls(req, resp)
        await self.handle_response(req, resp, errors_handler)


class FalconOpenAPIMiddleware:
    """OpenAPI middleware compatible with both WSGI and ASGI Falcon apps.

    This class delegates to transport-specific middleware implementations:
    :class:`FalconWSGIOpenAPIMiddleware` for sync hooks and
    :class:`FalconASGIOpenAPIMiddleware` for async hooks.
    """

    def __init__(
        self,
        openapi: OpenAPI,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        request_async_cls: Any = _DEFAULT_ASYNC,
        response_async_cls: Any = _DEFAULT_ASYNC,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **kwargs: Any,
    ):
        if request_async_cls is _DEFAULT_ASYNC:
            request_async_cls = FalconAsgiOpenAPIRequest
        if response_async_cls is _DEFAULT_ASYNC:
            response_async_cls = (
                FalconAsgiOpenAPIResponse if response_cls is not None else None
            )

        self.wsgi_middleware = FalconWSGIOpenAPIMiddleware(
            openapi,
            request_cls=request_cls,
            response_cls=response_cls,
            errors_handler_cls=errors_handler_cls,
            **kwargs,
        )
        self.asgi_middleware = FalconASGIOpenAPIMiddleware(
            openapi,
            request_cls=cast(
                Type[FalconAsgiOpenAPIRequest], request_async_cls
            ),
            response_cls=cast(
                Optional[Type[FalconAsgiOpenAPIResponse]],
                response_async_cls,
            ),
            errors_handler_cls=errors_handler_cls,
            **kwargs,
        )

    @classmethod
    def from_spec(
        cls,
        spec: SchemaPath,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        request_async_cls: Any = _DEFAULT_ASYNC,
        response_async_cls: Any = _DEFAULT_ASYNC,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **kwargs: Any,
    ) -> "FalconOpenAPIMiddleware":
        openapi = OpenAPI.build(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
        )
        return cls(
            openapi,
            request_cls=request_cls,
            response_cls=response_cls,
            request_async_cls=request_async_cls,
            response_async_cls=response_async_cls,
            errors_handler_cls=errors_handler_cls,
            **kwargs,
        )

    def process_request(self, req: Request, resp: Response) -> None:
        self.wsgi_middleware.process_request(req, resp)

    def process_response(
        self, req: Request, resp: Response, resource: Any, req_succeeded: bool
    ) -> None:
        self.wsgi_middleware.process_response(
            req,
            resp,
            resource,
            req_succeeded,
        )

    async def process_request_async(
        self, req: Request, resp: Response
    ) -> None:
        await self.asgi_middleware.process_request_async(req, resp)

    async def process_response_async(
        self,
        req: Request,
        resp: Response,
        resource: Any,
        req_succeeded: bool,
    ) -> None:
        await self.asgi_middleware.process_response_async(
            req,
            resp,
            resource,
            req_succeeded,
        )
