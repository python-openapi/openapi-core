"""OpenAPI core validation request validators module"""
from six import iteritems

from openapi_core.schema.exceptions import OpenAPIMappingError
from openapi_core.schema.parameters.exceptions import MissingParameter
from openapi_core.validation.request.models import (
    RequestParameters, RequestValidationResult,
)
from openapi_core.validation.util import get_operation_pattern


class RequestValidator(object):

    def __init__(self, spec, custom_formatters=None):
        self.spec = spec
        self.custom_formatters = custom_formatters

    def validate(self, request):
        try:
            server = self.spec.get_server(request.full_url_pattern)
        # don't process if server errors
        except OpenAPIMappingError as exc:
            return RequestValidationResult([exc, ], None, None)

        operation_pattern = get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

        try:
            operation = self.spec.get_operation(
                operation_pattern, request.method)
        # don't process if operation errors
        except OpenAPIMappingError as exc:
            return RequestValidationResult([exc, ], None, None)

        params, params_errors = self._get_parameters(request, operation)
        body, body_errors = self._get_body(request, operation)

        errors = params_errors + body_errors
        return RequestValidationResult(errors, body, params)

    def _get_parameters(self, request, operation):
        errors = []

        parameters = RequestParameters()
        for param_name, param in iteritems(operation.parameters):
            try:
                raw_value = param.get_value(request)
            except MissingParameter:
                continue
            except OpenAPIMappingError as exc:
                errors.append(exc)
                continue

            try:
                value = param.unmarshal(raw_value, self.custom_formatters)
            except OpenAPIMappingError as exc:
                errors.append(exc)
            else:
                parameters[param.location.value][param_name] = value

        return parameters, errors

    def _get_body(self, request, operation):
        errors = []

        if operation.request_body is None:
            return None, errors

        body = None
        try:
            media_type = operation.request_body[request.mimetype]
        except OpenAPIMappingError as exc:
            errors.append(exc)
        else:
            try:
                raw_body = operation.request_body.get_value(request)
            except OpenAPIMappingError as exc:
                errors.append(exc)
            else:
                try:
                    body = media_type.unmarshal(raw_body, self.custom_formatters)
                except OpenAPIMappingError as exc:
                    errors.append(exc)

        return body, errors
