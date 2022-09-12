"""OpenAPI core contrib flask decorators module"""
from functools import wraps
from typing import Any
from typing import Callable
from typing import Type

from flask.globals import request
from flask.wrappers import Request
from flask.wrappers import Response

from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequest
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponse
from openapi_core.spec import Spec
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.response import openapi_response_validator
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import ResponseValidator


class FlaskOpenAPIViewDecorator(OpenAPIProcessor):
    def __init__(
        self,
        spec: Spec,
        request_validator: RequestValidator,
        response_validator: ResponseValidator,
        request_class: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_class: Type[FlaskOpenAPIResponse] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        openapi_errors_handler: Type[
            FlaskOpenAPIErrorsHandler
        ] = FlaskOpenAPIErrorsHandler,
    ):
        super().__init__(request_validator, response_validator)
        self.spec = spec
        self.request_class = request_class
        self.response_class = response_class
        self.request_provider = request_provider
        self.openapi_errors_handler = openapi_errors_handler

    def __call__(self, view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def decorated(*args: Any, **kwargs: Any) -> Response:
            request = self._get_request()
            openapi_request = self._get_openapi_request(request)
            request_result = self.process_request(self.spec, openapi_request)
            if request_result.errors:
                return self._handle_request_errors(request_result)
            response = self._handle_request_view(
                request_result, view, *args, **kwargs
            )
            openapi_response = self._get_openapi_response(response)
            response_result = self.process_response(
                self.spec, openapi_request, openapi_response
            )
            if response_result.errors:
                return self._handle_response_errors(response_result)
            return response

        return decorated

    def _handle_request_view(
        self,
        request_result: RequestValidationResult,
        view: Callable[[Any], Response],
        *args: Any,
        **kwargs: Any
    ) -> Response:
        request = self._get_request()
        request.openapi = request_result  # type: ignore
        return view(*args, **kwargs)

    def _handle_request_errors(
        self, request_result: RequestValidationResult
    ) -> Response:
        return self.openapi_errors_handler.handle(request_result.errors)

    def _handle_response_errors(
        self, response_result: ResponseValidationResult
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
        request_class: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_class: Type[FlaskOpenAPIResponse] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        openapi_errors_handler: Type[
            FlaskOpenAPIErrorsHandler
        ] = FlaskOpenAPIErrorsHandler,
    ) -> "FlaskOpenAPIViewDecorator":
        return cls(
            spec,
            request_validator=openapi_request_validator,
            response_validator=openapi_response_validator,
            request_class=request_class,
            response_class=response_class,
            request_provider=request_provider,
            openapi_errors_handler=openapi_errors_handler,
        )
