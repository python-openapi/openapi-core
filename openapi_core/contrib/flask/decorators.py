"""OpenAPI core contrib flask decorators module"""
from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequest
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponse
from openapi_core.validation.decorators import OpenAPIDecorator
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator


class FlaskOpenAPIViewDecorator(OpenAPIDecorator):
    def __init__(
        self,
        spec,
        request_validator,
        response_validator,
        request_class=FlaskOpenAPIRequest,
        response_class=FlaskOpenAPIResponse,
        request_provider=FlaskRequestProvider,
        openapi_errors_handler=FlaskOpenAPIErrorsHandler,
    ):
        super().__init__(
            spec,
            request_validator,
            response_validator,
            request_class,
            response_class,
            request_provider,
            openapi_errors_handler,
        )

    def _handle_request_view(self, request_result, view, *args, **kwargs):
        request = self._get_request(*args, **kwargs)
        request.openapi = request_result
        return super()._handle_request_view(
            request_result, view, *args, **kwargs
        )

    @classmethod
    def from_spec(
        cls,
        spec,
        request_class=FlaskOpenAPIRequest,
        response_class=FlaskOpenAPIResponse,
        request_provider=FlaskRequestProvider,
        openapi_errors_handler=FlaskOpenAPIErrorsHandler,
    ):
        return cls(
            spec,
            request_validator=openapi_request_validator,
            response_validator=openapi_response_validator,
            request_class=request_class,
            response_class=response_class,
            request_provider=request_provider,
            openapi_errors_handler=openapi_errors_handler,
        )
