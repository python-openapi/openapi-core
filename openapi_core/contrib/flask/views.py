"""OpenAPI core contrib flask views module"""
from typing import Any

from flask.views import MethodView
from jsonschema_path import SchemaPath

from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler


class FlaskOpenAPIView(MethodView):
    """Brings OpenAPI specification validation and unmarshalling for views."""

    openapi_errors_handler = FlaskOpenAPIErrorsHandler

    def __init__(self, spec: SchemaPath, **unmarshaller_kwargs: Any):
        super().__init__()

        self.decorator = FlaskOpenAPIViewDecorator(
            spec,
            errors_handler_cls=self.openapi_errors_handler,
            **unmarshaller_kwargs,
        )

    def dispatch_request(self, *args: Any, **kwargs: Any) -> Any:
        response = self.decorator(super().dispatch_request)(*args, **kwargs)

        return response
