"""OpenAPI core validation request validators module"""
from six import iteritems

from openapi_core.exceptions import (
    OpenAPIMappingError, MissingParameter, MissingBody,
)
from openapi_core.validation.request.models import (
    RequestParameters, RequestValidationResult,
)
from openapi_core.validation.util import get_operation_pattern


class RequestValidator(object):

    def __init__(self, spec):
        self.spec = spec

    def validate(self, request):
        errors = []
        body = None
        parameters = RequestParameters()

        try:
            server = self.spec.get_server(request.full_url_pattern)
        # don't process if server errors
        except OpenAPIMappingError as exc:
            errors.append(exc)
            return RequestValidationResult(errors, body, parameters)

        operation_pattern = get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

        try:
            operation = self.spec.get_operation(
                operation_pattern, request.method)
        # don't process if operation errors
        except OpenAPIMappingError as exc:
            errors.append(exc)
            return RequestValidationResult(errors, body, parameters)

        for param_name, param in iteritems(operation.parameters):
            try:
                raw_value = self._get_raw_value(request, param)
            except MissingParameter as exc:
                if param.required:
                    errors.append(exc)

                if not param.schema or param.schema.default is None:
                    continue
                raw_value = param.schema.default

            try:
                value = param.unmarshal(raw_value)
            except OpenAPIMappingError as exc:
                errors.append(exc)
            else:
                parameters[param.location.value][param_name] = value

        if operation.request_body is not None:
            try:
                media_type = operation.request_body[request.mimetype]
            except OpenAPIMappingError as exc:
                errors.append(exc)
            else:
                try:
                    raw_body = self._get_raw_body(request)
                except MissingBody as exc:
                    if operation.request_body.required:
                        errors.append(exc)
                else:
                    try:
                        body = media_type.unmarshal(raw_body)
                    except OpenAPIMappingError as exc:
                        errors.append(exc)

        return RequestValidationResult(errors, body, parameters)

    def _get_raw_value(self, request, param):
        location = request.parameters[param.location.value]

        try:
            raw = location[param.name]
        except KeyError:
            raise MissingParameter(
                "Missing required `{0}` parameter".format(param.name))

        if param.aslist and param.explode:
            return location.getlist(param.name)

        return raw

    def _get_raw_body(self, request):
        if not request.body:
            raise MissingBody("Missing required request body")

        return request.body
