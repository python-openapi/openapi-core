"""OpenAPI core contrib django middlewares module"""
from typing import Callable

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from openapi_core.contrib.django.handlers import DjangoOpenAPIErrorsHandler
from openapi_core.contrib.django.handlers import (
    DjangoOpenAPIValidRequestHandler,
)
from openapi_core.contrib.django.requests import DjangoOpenAPIRequest
from openapi_core.contrib.django.responses import DjangoOpenAPIResponse
from openapi_core.unmarshalling.processors import UnmarshallingProcessor


class DjangoOpenAPIMiddleware(
    UnmarshallingProcessor[HttpRequest, HttpResponse]
):
    request_cls = DjangoOpenAPIRequest
    response_cls = DjangoOpenAPIResponse
    valid_request_handler_cls = DjangoOpenAPIValidRequestHandler
    errors_handler = DjangoOpenAPIErrorsHandler()

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

        if not hasattr(settings, "OPENAPI_SPEC"):
            raise ImproperlyConfigured("OPENAPI_SPEC not defined in settings")

        if hasattr(settings, "OPENAPI_RESPONSE_CLS"):
            self.response_cls = settings.OPENAPI_RESPONSE_CLS

        super().__init__(settings.OPENAPI_SPEC)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        valid_request_handler = self.valid_request_handler_cls(
            request, self.get_response
        )
        response = self.handle_request(
            request, valid_request_handler, self.errors_handler
        )

        return self.handle_response(request, response, self.errors_handler)

    def _get_openapi_request(
        self, request: HttpRequest
    ) -> DjangoOpenAPIRequest:
        return self.request_cls(request)

    def _get_openapi_response(
        self, response: HttpResponse
    ) -> DjangoOpenAPIResponse:
        assert self.response_cls is not None
        return self.response_cls(response)

    def _validate_response(self) -> bool:
        return self.response_cls is not None
