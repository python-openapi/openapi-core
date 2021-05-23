"""OpenAPI core contrib flask decorators module"""
from functools import wraps
from typing import Any, Callable, Type

from flask import Request, Response

from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequestFactory
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponseFactory
from openapi_core.spec.paths import SpecPath
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest, RequestValidationResult,
)
from openapi_core.validation.request.factories import BaseOpenAPIRequestFactory
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import (
    OpenAPIResponse, ResponseValidationResult,
)
from openapi_core.validation.response.factories import (
    BaseOpenAPIResponseFactory,
)
from openapi_core.validation.response.validators import ResponseValidator


class FlaskOpenAPIViewDecorator:

    def __init__(
        self,
        openapi_validation_processor: OpenAPIProcessor,
        openapi_request_factory: FlaskOpenAPIRequestFactory,
        openapi_response_factory: FlaskOpenAPIResponseFactory,
        request_provider: FlaskRequestProvider,
        openapi_errors_handler: FlaskOpenAPIErrorsHandler,
    ):
        self.openapi_validation_processor = openapi_validation_processor
        self.openapi_request_factory = openapi_request_factory
        self.openapi_response_factory = openapi_response_factory
        self.request_provider = request_provider
        self.openapi_errors_handler = openapi_errors_handler

    @classmethod
    def from_spec(
        cls,
        spec: SpecPath,
    ) -> 'FlaskOpenAPIViewDecorator':
        openapi_validation_processor = OpenAPIProcessor.from_spec(spec)
        openapi_request_factory = FlaskOpenAPIRequestFactory()
        openapi_response_factory = FlaskOpenAPIResponseFactory()
        request_provider = FlaskRequestProvider()
        openapi_errors_handler = FlaskOpenAPIErrorsHandler()
        return cls(
            openapi_validation_processor=openapi_validation_processor,
            openapi_request_factory=openapi_request_factory,
            openapi_response_factory=openapi_response_factory,
            request_provider=request_provider,
            openapi_errors_handler=openapi_errors_handler,
        )

    def __call__(self, view: Callable[..., Response]):
        @wraps(view)
        def decorated(*args, **kwargs):
            request = self._get_request(*args, **kwargs)
            openapi_request = self._get_openapi_request(request)
            request_result = self._process_openapi_request(openapi_request)
            if request_result.errors:
                return self._handle_request_errors(request_result)
            response = self._handle_request_view(
                request_result, view, *args, **kwargs)
            openapi_response = self._get_openapi_response(response)
            response_result = self._process_openapi_response(
                openapi_request, openapi_response)
            if response_result.errors:
                return self._handle_response_errors(response_result)
            return response
        return decorated

    def _get_request(self, *args, **kwargs) -> Request:
        return self.request_provider.provide(*args, **kwargs)

    def _handle_request_view(
        self,
        request_result: RequestValidationResult,
        view: Callable[..., Response],
        *args, **kwargs,
    ) -> Response:
        request = self._get_request(*args, **kwargs)
        request.openapi = request_result  # type: ignore
        return view(*args, **kwargs)

    def _handle_request_errors(
        self,
        request_result: RequestValidationResult,
    ) -> Response:
        return self.openapi_errors_handler.handle(request_result.errors)

    def _handle_response_errors(
        self,
        response_result: ResponseValidationResult,
    ) -> Response:
        return self.openapi_errors_handler.handle(response_result.errors)

    def _get_openapi_request(self, request) -> OpenAPIRequest:
        return self.openapi_request_factory.create(request)

    def _get_openapi_response(self, response) -> OpenAPIResponse:
        return self.openapi_response_factory.create(response)

    def _process_openapi_request(
        self,
        request: OpenAPIRequest,
    ) -> RequestValidationResult:
        return self.openapi_validation_processor.process_openapi_request(
            request)

    def _process_openapi_response(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> ResponseValidationResult:
        return self.openapi_validation_processor.process_openapi_response(
            request, response)
