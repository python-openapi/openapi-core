"""OpenAPI core contrib flask decorators module"""

from functools import wraps
from typing import Any
from typing import Callable
from typing import Type

from flask.globals import request
from flask.wrappers import Request
from flask.wrappers import Response
from jsonschema_path import SchemaPath

from openapi_core import OpenAPI
from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.handlers import FlaskOpenAPIValidRequestHandler
from openapi_core.contrib.flask.integrations import FlaskIntegration
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequest
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponse


class FlaskOpenAPIViewDecorator(FlaskIntegration):
    valid_request_handler_cls = FlaskOpenAPIValidRequestHandler
    errors_handler_cls: Type[FlaskOpenAPIErrorsHandler] = (
        FlaskOpenAPIErrorsHandler
    )

    def __init__(
        self,
        openapi: OpenAPI,
        request_cls: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_cls: Type[FlaskOpenAPIResponse] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        errors_handler_cls: Type[
            FlaskOpenAPIErrorsHandler
        ] = FlaskOpenAPIErrorsHandler,
    ):
        super().__init__(openapi)
        self.request_cls = request_cls
        self.response_cls = response_cls
        self.request_provider = request_provider
        self.errors_handler_cls = errors_handler_cls

    def __call__(self, view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def decorated(*args: Any, **kwargs: Any) -> Response:
            request = self.get_request()
            valid_request_handler = self.valid_request_handler_cls(
                request, view, *args, **kwargs
            )
            errors_handler = self.errors_handler_cls()
            response = self.handle_request(
                request, valid_request_handler, errors_handler
            )
            return self.handle_response(request, response, errors_handler)

        return decorated

    def get_request(self) -> Request:
        return request

    @classmethod
    def from_spec(
        cls,
        spec: SchemaPath,
        request_cls: Type[FlaskOpenAPIRequest] = FlaskOpenAPIRequest,
        response_cls: Type[FlaskOpenAPIResponse] = FlaskOpenAPIResponse,
        request_provider: Type[FlaskRequestProvider] = FlaskRequestProvider,
        errors_handler_cls: Type[
            FlaskOpenAPIErrorsHandler
        ] = FlaskOpenAPIErrorsHandler,
    ) -> "FlaskOpenAPIViewDecorator":
        openapi = OpenAPI(spec)
        return cls(
            openapi,
            request_cls=request_cls,
            response_cls=response_cls,
            request_provider=request_provider,
            errors_handler_cls=errors_handler_cls,
        )
