"""OpenAPI core validation decorators module"""
from functools import wraps

from openapi_core.validation.processors import OpenAPIProcessor


class OpenAPIDecorator(OpenAPIProcessor):

    def __init__(
            self,
            request_validator,
            response_validator,
            request_factory,
            response_factory,
            request_provider,
            openapi_errors_handler,
    ):
        super(OpenAPIDecorator, self).__init__(
            request_validator, response_validator)
        self.request_factory = request_factory
        self.response_factory = response_factory
        self.request_provider = request_provider
        self.openapi_errors_handler = openapi_errors_handler

    def __call__(self, view):
        @wraps(view)
        def decorated(*args, **kwargs):
            request = self._get_request(*args, **kwargs)
            openapi_request = self._get_openapi_request(request)
            errors = self.process_request(openapi_request)
            if errors:
                return self._handle_openapi_errors(errors)
            response = view(*args, **kwargs)
            openapi_response = self._get_openapi_response(response)
            errors = self.process_response(openapi_request, openapi_response)
            if errors:
                return self._handle_openapi_errors(errors)
            return response
        return decorated

    def _get_request(self, *args, **kwargs):
        return self.request_provider.provide(*args, **kwargs)

    def _handle_openapi_errors(self, errors):
        return self.openapi_errors_handler.handle(errors)

    def _get_openapi_request(self, request):
        return self.request_factory.create(request)

    def _get_openapi_response(self, response):
        return self.response_factory.create(response)
