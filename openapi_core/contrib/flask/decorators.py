"""OpenAPI core contrib flask decorators module"""
from typing import Optional

from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequestFactory
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponseFactory
from openapi_core.spec.paths import SpecPath
from openapi_core.validation.decorators import OpenAPIDecorator
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class FlaskOpenAPIViewDecorator(OpenAPIDecorator):

    def __init__(
        self,
        request_validator: RequestValidator,
        response_validator: ResponseValidator,
        request_factory: Optional[FlaskOpenAPIRequestFactory] = None,
        response_factory: Optional[FlaskOpenAPIResponseFactory] = None,
        request_provider: Optional[FlaskRequestProvider] = None,
        errors_handler: Optional[FlaskOpenAPIErrorsHandler] = None,
    ):
        request_factory = request_factory or FlaskOpenAPIRequestFactory()
        response_factory = response_factory or FlaskOpenAPIResponseFactory()
        errors_handler = errors_handler or FlaskOpenAPIErrorsHandler()
        super().__init__(
            request_validator, response_validator,
            request_factory, response_factory,
            request_provider, errors_handler,
        )

    def _handle_request_view(self, request_result, view, *args, **kwargs):
        request = self._get_request(*args, **kwargs)
        request.openapi = request_result
        return super()._handle_request_view(
            request_result, view, *args, **kwargs)

    @classmethod
    def from_spec(
        cls,
        spec: SpecPath,
        request_factory: Optional[FlaskOpenAPIRequestFactory] = None,
        response_factory: Optional[FlaskOpenAPIResponseFactory] = None,
        request_provider: Optional[FlaskRequestProvider] = None,
        errors_handler: Optional[FlaskOpenAPIErrorsHandler] = None,
    ) -> 'FlaskOpenAPIViewDecorator':
        request_validator = RequestValidator(spec)
        response_validator = ResponseValidator(spec)
        return cls(
            request_validator=request_validator,
            response_validator=response_validator,
            request_factory=request_factory,
            response_factory=response_factory,
            request_provider=request_provider,
            errors_handler=errors_handler,
        )
