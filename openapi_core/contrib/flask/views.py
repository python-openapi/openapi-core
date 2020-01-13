"""OpenAPI core contrib flask views module"""
from flask.views import MethodView

from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class FlaskOpenAPIView(MethodView):
    """Brings OpenAPI specification validation and unmarshalling for views."""

    def __init__(self, request_validator, response_validator):
        super(MethodView, self).__init__()
        self.request_validator = request_validator
        self.response_validator = response_validator

    def dispatch_request(self, *args, **kwargs):
        decorator = FlaskOpenAPIViewDecorator(
            request_validator=self.request_validator,
            response_validator=self.response_validator,
            openapi_errors_handler=self.handle_openapi_errors,
        )
        return decorator(super(FlaskOpenAPIView, self).dispatch_request)(
            *args, **kwargs)

    def handle_openapi_errors(self, errors):
        """Handles OpenAPI request/response errors.

        Should return response object::

            class MyView(FlaskOpenAPIView):

                def handle_openapi_errors(self, errors):
                    return jsonify({'errors': errors})
        """
        raise NotImplementedError

    @classmethod
    def from_spec(cls, spec):
        request_validator = RequestValidator(spec)
        response_validator = ResponseValidator(spec)
        return cls(request_validator, response_validator)
