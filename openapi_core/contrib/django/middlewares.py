"""OpenAPI core contrib django middlewares module"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from openapi_core.contrib.django.handlers import DjangoOpenAPIErrorsHandler
from openapi_core.contrib.django.requests import DjangoOpenAPIRequestFactory
from openapi_core.contrib.django.responses import DjangoOpenAPIResponseFactory
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class DjangoOpenAPIMiddleware:

    request_factory = DjangoOpenAPIRequestFactory()
    response_factory = DjangoOpenAPIResponseFactory()
    errors_handler = DjangoOpenAPIErrorsHandler()

    def __init__(self, get_response):
        self.get_response = get_response

        if not hasattr(settings, "OPENAPI_SPEC"):
            raise ImproperlyConfigured("OPENAPI_SPEC not defined in settings")

        request_validator = RequestValidator(settings.OPENAPI_SPEC)
        response_validator = ResponseValidator(settings.OPENAPI_SPEC)
        self.validation_processor = OpenAPIProcessor(
            request_validator, response_validator
        )

    def __call__(self, request):
        openapi_request = self._get_openapi_request(request)
        req_result = self.validation_processor.process_request(openapi_request)
        if req_result.errors:
            response = self._handle_request_errors(req_result, request)
        else:
            request.openapi = req_result
            response = self.get_response(request)

        openapi_response = self._get_openapi_response(response)
        resp_result = self.validation_processor.process_response(
            openapi_request, openapi_response
        )
        if resp_result.errors:
            return self._handle_response_errors(resp_result, request, response)

        return response

    def _handle_request_errors(self, request_result, req):
        return self.errors_handler.handle(request_result.errors, req, None)

    def _handle_response_errors(self, response_result, req, resp):
        return self.errors_handler.handle(response_result.errors, req, resp)

    def _get_openapi_request(self, request):
        return self.request_factory.create(request)

    def _get_openapi_response(self, response):
        return self.response_factory.create(response)
