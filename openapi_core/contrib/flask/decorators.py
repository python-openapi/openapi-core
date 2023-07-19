"""OpenAPI core contrib flask decorators module"""
from functools import wraps
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type

from flask.globals import request
from flask.helpers import make_response
from flask.wrappers import Request
from flask.wrappers import Response

from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequest
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponse
from openapi_core.spec import Spec
from openapi_core.unmarshalling.processors import UnmarshallingProcessor
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType


class FlaskOpenAPIViewDecorator(UnmarshallingProcessor):
    def __init__(
        self,
        spec: Spec,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_class: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_class: Type[FlaskOpenAPIResponse] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        openapi_errors_handler: Type[
            FlaskOpenAPIErrorsHandler
        ] = FlaskOpenAPIErrorsHandler,
        **unmarshaller_kwargs: Any,
    ):
        super().__init__(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
            **unmarshaller_kwargs,
        )
        self.request_class = request_class
        self.response_class = response_class
        self.request_provider = request_provider
        self.openapi_errors_handler = openapi_errors_handler

    def __call__(self, view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def decorated(*args: Any, **kwargs: Any) -> Response:
            request = self._get_request()
            openapi_request = self._get_openapi_request(request)
            request_result = self.process_request(openapi_request)
            if request_result.errors:
                return self._handle_request_errors(request_result)
            response = self._handle_request_view(
                request_result, view, *args, **kwargs
            )
            openapi_response = self._get_openapi_response(response)
            response_result = self.process_response(
                openapi_request, openapi_response
            )
            if response_result.errors:
                return self._handle_response_errors(response_result)
            return response

        return decorated

    def _handle_request_view(
        self,
        request_result: RequestUnmarshalResult,
        view: Callable[[Any], Response],
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        request = self._get_request()
        request.openapi = request_result  # type: ignore
        rv = view(*args, **kwargs)
        return make_response(rv)

    def _handle_request_errors(
        self, request_result: RequestUnmarshalResult
    ) -> Response:
        return self.openapi_errors_handler.handle(request_result.errors)

    def _handle_response_errors(
        self, response_result: ResponseUnmarshalResult
    ) -> Response:
        return self.openapi_errors_handler.handle(response_result.errors)

    def _get_request(self) -> Request:
        return request

    def _get_openapi_request(self, request: Request) -> FlaskOpenAPIRequest:
        return self.request_class(request)

    def _get_openapi_response(
        self, response: Response
    ) -> FlaskOpenAPIResponse:
        return self.response_class(response)

    @classmethod
    def from_spec(
        cls,
        spec: Spec,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_class: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_class: Type[FlaskOpenAPIResponse] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        openapi_errors_handler: Type[
            FlaskOpenAPIErrorsHandler
        ] = FlaskOpenAPIErrorsHandler,
        **unmarshaller_kwargs: Any,
    ) -> "FlaskOpenAPIViewDecorator":
        return cls(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
            request_class=request_class,
            response_class=response_class,
            request_provider=request_provider,
            openapi_errors_handler=openapi_errors_handler,
            **unmarshaller_kwargs,
        )
