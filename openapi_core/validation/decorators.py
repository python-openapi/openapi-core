"""OpenAPI core validation decorators module"""
from functools import wraps

from openapi_core.validation.handlers import BaseOpenAPIErrorsHandler
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest, RequestValidationResult,
)
from openapi_core.validation.request.factories import BaseOpenAPIRequestFactory
from openapi_core.validation.request.providers import (
    BaseOpenAPIRequestProvider,
)
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import (
    OpenAPIResponse, ResponseValidationResult,
)
from openapi_core.validation.response.factories import (
    BaseOpenAPIResponseFactory,
)
from openapi_core.validation.response.validators import ResponseValidator


class OpenAPIDecorator(OpenAPIProcessor):

    def __init__(
            self,
            request_validator: RequestValidator,
            response_validator: ResponseValidator,
            request_factory: BaseOpenAPIRequestFactory,
            response_factory: BaseOpenAPIResponseFactory,
            request_provider: BaseOpenAPIRequestProvider,
            openapi_errors_handler: BaseOpenAPIErrorsHandler,
    ):
        super().__init__(request_validator, response_validator)
        self.request_factory = request_factory
        self.response_factory = response_factory
        self.request_provider = request_provider
        self.openapi_errors_handler = openapi_errors_handler

    def __call__(self, view):
        @wraps(view)
        def decorated(*args, **kwargs):
            request = self._get_request(*args, **kwargs)
            openapi_request = self._get_openapi_request(request)
            request_result = self.process_openapi_request(openapi_request)
            if request_result.errors:
                return self._handle_request_errors(request_result)
            response = self._handle_request_view(
                request_result, view, *args, **kwargs)
            openapi_response = self._get_openapi_response(response)
            response_result = self.process_openapi_response(
                openapi_request, openapi_response)
            if response_result.errors:
                return self._handle_response_errors(response_result)
            return response
        return decorated

    def _get_request(self, *args, **kwargs):
        return self.request_provider.provide(*args, **kwargs)

    def _handle_request_view(self, request_result, view, *args, **kwargs):
        return view(*args, **kwargs)

    def _handle_request_errors(
        self,
        request_result: RequestValidationResult,
    ) -> None:
        return self.openapi_errors_handler.handle(request_result.errors)

    def _handle_response_errors(
        self,
        response_result: ResponseValidationResult,
    ) -> None:
        return self.openapi_errors_handler.handle(response_result.errors)

    def _get_openapi_request(self, request) -> OpenAPIRequest:
        return self.request_factory.create(request)

    def _get_openapi_response(self, response) -> OpenAPIResponse:
        return self.response_factory.create(response)
