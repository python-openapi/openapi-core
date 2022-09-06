"""OpenAPI core validation decorators module"""
from functools import wraps

from openapi_core.validation.processors import OpenAPIProcessor


class OpenAPIDecorator(OpenAPIProcessor):
    def __init__(
        self,
        spec,
        request_validator,
        response_validator,
        request_class,
        response_class,
        request_provider,
        openapi_errors_handler,
    ):
        super().__init__(request_validator, response_validator)
        self.spec = spec
        self.request_class = request_class
        self.response_class = response_class
        self.request_provider = request_provider
        self.openapi_errors_handler = openapi_errors_handler

    def __call__(self, view):
        @wraps(view)
        def decorated(*args, **kwargs):
            request = self._get_request(*args, **kwargs)
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

    def _get_request(self, *args, **kwargs):
        return self.request_provider.provide(*args, **kwargs)

    def _handle_request_view(self, request_result, view, *args, **kwargs):
        return view(*args, **kwargs)

    def _handle_request_errors(self, request_result):
        return self.openapi_errors_handler.handle(request_result.errors)

    def _handle_response_errors(self, response_result):
        return self.openapi_errors_handler.handle(response_result.errors)

    def _get_openapi_request(self, request):
        return self.request_class(request)

    def _get_openapi_response(self, response):
        return self.response_class(response)
