"""OpenAPI core contrib falcon middlewares module"""
from typing import Any
from typing import Optional
from typing import Type

from falcon.request import Request
from falcon.response import Response

from openapi_core.contrib.falcon.handlers import FalconOpenAPIErrorsHandler
from openapi_core.contrib.falcon.handlers import (
    FalconOpenAPIValidRequestHandler,
)
from openapi_core.contrib.falcon.requests import FalconOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponse
from openapi_core.spec import Spec
from openapi_core.unmarshalling.processors import UnmarshallingProcessor
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType


class FalconOpenAPIMiddleware(UnmarshallingProcessor[Request, Response]):
    request_cls = FalconOpenAPIRequest
    response_cls = FalconOpenAPIResponse
    valid_request_handler_cls = FalconOpenAPIValidRequestHandler
    errors_handler_cls: Type[
        FalconOpenAPIErrorsHandler
    ] = FalconOpenAPIErrorsHandler

    def __init__(
        self,
        spec: Spec,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **unmarshaller_kwargs: Any,
    ):
        super().__init__(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
            **unmarshaller_kwargs,
        )
        self.request_cls = request_cls or self.request_cls
        self.response_cls = response_cls or self.response_cls
        self.errors_handler_cls = errors_handler_cls or self.errors_handler_cls

    @classmethod
    def from_spec(
        cls,
        spec: Spec,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **unmarshaller_kwargs: Any,
    ) -> "FalconOpenAPIMiddleware":
        return cls(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
            request_cls=request_cls,
            response_cls=response_cls,
            errors_handler_cls=errors_handler_cls,
            **unmarshaller_kwargs,
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

    def _get_openapi_request(self, request: Request) -> FalconOpenAPIRequest:
        return self.request_cls(request)

    def _get_openapi_response(
        self, response: Response
    ) -> FalconOpenAPIResponse:
        assert self.response_cls is not None
        return self.response_cls(response)

    def _validate_response(self) -> bool:
        return self.response_cls is not None
