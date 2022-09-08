"""OpenAPI core contrib flask views module"""
from typing import Any

from flask.views import MethodView

from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler
from openapi_core.spec import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator


class FlaskOpenAPIView(MethodView):
    """Brings OpenAPI specification validation and unmarshalling for views."""

    openapi_errors_handler = FlaskOpenAPIErrorsHandler

    def __init__(self, spec: Spec):
        super().__init__()
        self.spec = spec

    def dispatch_request(self, *args: Any, **kwargs: Any) -> Any:
        decorator = FlaskOpenAPIViewDecorator(
            self.spec,
            request_validator=openapi_request_validator,
            response_validator=openapi_response_validator,
            openapi_errors_handler=self.openapi_errors_handler,
        )
        return decorator(super().dispatch_request)(*args, **kwargs)
