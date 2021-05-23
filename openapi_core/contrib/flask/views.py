"""OpenAPI core contrib flask views module"""
from flask.views import MethodView

from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.contrib.flask.providers import FlaskRequestProvider
from openapi_core.contrib.flask.requests import FlaskOpenAPIRequestFactory
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponseFactory
from openapi_core.spec.paths import SpecPath
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class FlaskOpenAPIView(MethodView):
    """Brings OpenAPI specification validation and unmarshalling for views."""

    def __init__(self, spec: SpecPath):
        super().__init__()
        self.spec = spec

    @property
    def decorator(self) -> FlaskOpenAPIViewDecorator:
        return FlaskOpenAPIViewDecorator.from_spec(self.spec)

    def dispatch_request(self, *args, **kwargs):
        return self.decorator(super().dispatch_request)(*args, **kwargs)
