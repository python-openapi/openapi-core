"""OpenAPI core contrib flask views module"""

from typing import Any

from flask.views import MethodView

from openapi_core import OpenAPI
from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
from openapi_core.contrib.flask.handlers import FlaskOpenAPIErrorsHandler


class FlaskOpenAPIView(MethodView):
    """Brings OpenAPI specification validation and unmarshalling for views."""

    openapi_errors_handler = FlaskOpenAPIErrorsHandler

    def __init__(self, openapi: OpenAPI):
        super().__init__()

        self.decorator = FlaskOpenAPIViewDecorator(
            openapi,
            errors_handler_cls=self.openapi_errors_handler,
        )

    def dispatch_request(self, *args: Any, **kwargs: Any) -> Any:
        response = self.decorator(super().dispatch_request)(*args, **kwargs)

        return response
