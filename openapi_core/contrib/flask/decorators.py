"""OpenAPI core contrib flask decorators module"""
from functools import wraps
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type

from flask.globals import request
from flask.wrappers import Request
from flask.wrappers import Response
from jsonschema_path import SchemaPath

from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.handlers import FlaskOpenAPIValidRequestHandler
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequest
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponse
from openapi_core.unmarshalling.processors import UnmarshallingProcessor
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType


class FlaskOpenAPIViewDecorator(UnmarshallingProcessor[Request, Response]):
    valid_request_handler_cls = FlaskOpenAPIValidRequestHandler
    errors_handler_cls: Type[
        FlaskOpenAPIErrorsHandler
    ] = FlaskOpenAPIErrorsHandler

    def __init__(
        self,
        spec: SchemaPath,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_cls: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_cls: Optional[
            Type[FlaskOpenAPIResponse]
        ] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        errors_handler_cls: Type[
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
        self.request_cls = request_cls
        self.response_cls = response_cls
        self.request_provider = request_provider
        self.errors_handler_cls = errors_handler_cls

    def __call__(self, view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def decorated(*args: Any, **kwargs: Any) -> Response:
            request = self._get_request()
            valid_request_handler = self.valid_request_handler_cls(
                request, view, *args, **kwargs
            )
            errors_handler = self.errors_handler_cls()
            response = self.handle_request(
                request, valid_request_handler, errors_handler
            )
            return self.handle_response(request, response, errors_handler)

        return decorated

    def _get_request(self) -> Request:
        return request

    def _get_openapi_request(self, request: Request) -> FlaskOpenAPIRequest:
        return self.request_cls(request)

    def _get_openapi_response(
        self, response: Response
    ) -> FlaskOpenAPIResponse:
        assert self.response_cls is not None
        return self.response_cls(response)

    def _validate_response(self) -> bool:
        return self.response_cls is not None

    @classmethod
    def from_spec(
        cls,
        spec: SchemaPath,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        request_cls: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_cls: Type[FlaskOpenAPIResponse] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        errors_handler_cls: Type[
            FlaskOpenAPIErrorsHandler
        ] = FlaskOpenAPIErrorsHandler,
        **unmarshaller_kwargs: Any,
    ) -> "FlaskOpenAPIViewDecorator":
        return cls(
            spec,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
            request_cls=request_cls,
            response_cls=response_cls,
            request_provider=request_provider,
            errors_handler_cls=errors_handler_cls,
            **unmarshaller_kwargs,
        )
