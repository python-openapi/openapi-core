"""OpenAPI core contrib django decorators module"""

from typing import Any
from typing import Callable
from typing import Optional
from typing import Type

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from jsonschema_path import SchemaPath

from openapi_core import OpenAPI
from openapi_core.contrib.django.handlers import DjangoOpenAPIErrorsHandler
from openapi_core.contrib.django.handlers import (
    DjangoOpenAPIValidRequestHandler,
)
from openapi_core.contrib.django.integrations import DjangoIntegration
from openapi_core.contrib.django.providers import get_default_openapi_instance
from openapi_core.contrib.django.requests import DjangoOpenAPIRequest
from openapi_core.contrib.django.responses import DjangoOpenAPIResponse


class DjangoOpenAPIViewDecorator(DjangoIntegration):
    valid_request_handler_cls = DjangoOpenAPIValidRequestHandler
    errors_handler_cls: Type[DjangoOpenAPIErrorsHandler] = (
        DjangoOpenAPIErrorsHandler
    )

    def __init__(
        self,
        openapi: Optional[OpenAPI] = None,
        request_cls: Type[DjangoOpenAPIRequest] = DjangoOpenAPIRequest,
        response_cls: Type[DjangoOpenAPIResponse] = DjangoOpenAPIResponse,
        errors_handler_cls: Type[
            DjangoOpenAPIErrorsHandler
        ] = DjangoOpenAPIErrorsHandler,
    ):
        if openapi is None:
            openapi = get_default_openapi_instance()

        super().__init__(openapi)

        # If OPENAPI_RESPONSE_CLS is defined in settings.py (for custom response classes),
        # set the response_cls accordingly.
        if hasattr(settings, "OPENAPI_RESPONSE_CLS"):
            response_cls = settings.OPENAPI_RESPONSE_CLS

        self.request_cls = request_cls
        self.response_cls = response_cls

    def __call__(self, view_func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Thanks to this method, the class acts as a decorator.
        Example usage:

            @DjangoOpenAPIViewDecorator()
            def my_view(request): ...

        """

        def _wrapped_view(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            # get_response is the function that we treats
            # as the "next step" in the chain (i.e., our original view).
            def get_response(r: HttpRequest) -> HttpResponse:
                return view_func(r, *args, **kwargs)

            # Create a handler that will validate the request.
            valid_request_handler = self.valid_request_handler_cls(
                request, get_response
            )

            # Validate the request (before running the view).
            errors_handler = self.errors_handler_cls()
            response = self.handle_request(
                request, valid_request_handler, errors_handler
            )

            # Validate the response (after the view) if should_validate_response() returns True.
            return self.handle_response(request, response, errors_handler)

        return _wrapped_view

    @classmethod
    def from_spec(
        cls,
        spec: SchemaPath,
        request_cls: Type[DjangoOpenAPIRequest] = DjangoOpenAPIRequest,
        response_cls: Type[DjangoOpenAPIResponse] = DjangoOpenAPIResponse,
        errors_handler_cls: Type[
            DjangoOpenAPIErrorsHandler
        ] = DjangoOpenAPIErrorsHandler,
    ) -> "DjangoOpenAPIViewDecorator":
        openapi = OpenAPI(spec)
        return cls(
            openapi,
            request_cls=request_cls,
            response_cls=response_cls,
            errors_handler_cls=errors_handler_cls,
        )
