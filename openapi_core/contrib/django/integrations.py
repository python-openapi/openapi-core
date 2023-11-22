from django.http.request import HttpRequest
from django.http.response import HttpResponse

from openapi_core.contrib.django.requests import DjangoOpenAPIRequest
from openapi_core.contrib.django.responses import DjangoOpenAPIResponse
from openapi_core.unmarshalling.processors import UnmarshallingProcessor
from openapi_core.unmarshalling.typing import ErrorsHandlerCallable


class DjangoIntegration(UnmarshallingProcessor[HttpRequest, HttpResponse]):
    request_cls = DjangoOpenAPIRequest
    response_cls = DjangoOpenAPIResponse

    def get_openapi_request(
        self, request: HttpRequest
    ) -> DjangoOpenAPIRequest:
        return self.request_cls(request)

    def get_openapi_response(
        self, response: HttpResponse
    ) -> DjangoOpenAPIResponse:
        assert self.response_cls is not None
        return self.response_cls(response)

    def should_validate_response(self) -> bool:
        return self.response_cls is not None

    def handle_response(
        self,
        request: HttpRequest,
        response: HttpResponse,
        errors_handler: ErrorsHandlerCallable[HttpResponse],
    ) -> HttpResponse:
        if not self.should_validate_response():
            return response
        return super().handle_response(request, response, errors_handler)
