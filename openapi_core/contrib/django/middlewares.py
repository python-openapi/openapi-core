"""OpenAPI core contrib django middlewares module"""

from typing import Callable

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from openapi_core.contrib.django.handlers import DjangoOpenAPIErrorsHandler
from openapi_core.contrib.django.handlers import (
    DjangoOpenAPIValidRequestHandler,
)
from openapi_core.contrib.django.integrations import DjangoIntegration
from openapi_core.contrib.django.providers import get_default_openapi_instance


class DjangoOpenAPIMiddleware(DjangoIntegration):
    valid_request_handler_cls = DjangoOpenAPIValidRequestHandler
    errors_handler = DjangoOpenAPIErrorsHandler()

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

        if hasattr(settings, "OPENAPI_RESPONSE_CLS"):
            self.response_cls = settings.OPENAPI_RESPONSE_CLS

        openapi = get_default_openapi_instance()

        super().__init__(openapi)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        valid_request_handler = self.valid_request_handler_cls(
            request, self.get_response
        )
        response = self.handle_request(
            request, valid_request_handler, self.errors_handler
        )

        return self.handle_response(request, response, self.errors_handler)
