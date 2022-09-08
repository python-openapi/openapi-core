"""OpenAPI core contrib django middlewares module"""
from typing import Callable

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from openapi_core.contrib.django.handlers import DjangoOpenAPIErrorsHandler
from openapi_core.contrib.django.requests import DjangoOpenAPIRequest
from openapi_core.contrib.django.responses import DjangoOpenAPIResponse
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.response import openapi_response_validator
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import Response


class DjangoOpenAPIMiddleware:

    request_class = DjangoOpenAPIRequest
    response_class = DjangoOpenAPIResponse
    errors_handler = DjangoOpenAPIErrorsHandler()

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

        if not hasattr(settings, "OPENAPI_SPEC"):
            raise ImproperlyConfigured("OPENAPI_SPEC not defined in settings")

        self.validation_processor = OpenAPIProcessor(
            openapi_request_validator, openapi_response_validator
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        openapi_request = self._get_openapi_request(request)
        req_result = self.validation_processor.process_request(
            settings.OPENAPI_SPEC, openapi_request
        )
        if req_result.errors:
            response = self._handle_request_errors(req_result, request)
        else:
            request.openapi = req_result
            response = self.get_response(request)

        openapi_response = self._get_openapi_response(response)
        resp_result = self.validation_processor.process_response(
            settings.OPENAPI_SPEC, openapi_request, openapi_response
        )
        if resp_result.errors:
            return self._handle_response_errors(resp_result, request, response)

        return response

    def _handle_request_errors(
        self, request_result: RequestValidationResult, req: HttpRequest
    ) -> JsonResponse:
        return self.errors_handler.handle(request_result.errors, req, None)

    def _handle_response_errors(
        self,
        response_result: ResponseValidationResult,
        req: HttpRequest,
        resp: HttpResponse,
    ) -> JsonResponse:
        return self.errors_handler.handle(response_result.errors, req, resp)

    def _get_openapi_request(
        self, request: HttpRequest
    ) -> DjangoOpenAPIRequest:
        return self.request_class(request)

    def _get_openapi_response(
        self, response: HttpResponse
    ) -> DjangoOpenAPIResponse:
        return self.response_class(response)
