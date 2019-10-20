"""OpenAPI core validation request validators module"""
from itertools import chain
from six import iteritems

from openapi_core.schema.media_types.exceptions import (
    InvalidMediaTypeValue, InvalidContentType,
)
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.parameters.exceptions import (
    OpenAPIParameterError, MissingRequiredParameter,
)
from openapi_core.schema.paths.exceptions import InvalidPath
from openapi_core.schema.request_bodies.exceptions import MissingRequestBody
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.validation.request.datatypes import (
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
        except InvalidServer as exc:
            return RequestValidationResult([exc, ], None, None)

        operation_pattern = get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

        try:
            path = self.spec[operation_pattern]
        except InvalidPath as exc:
            return RequestValidationResult([exc, ], None, None)

        try:
            operation = self.spec.get_operation(
                operation_pattern, request.method)
        # don't process if operation errors
        except InvalidOperation as exc:
            return RequestValidationResult([exc, ], None, None)

        params, params_errors = self._get_parameters(
            request, chain(
                iteritems(operation.parameters),
                iteritems(path.parameters)
            )
        )

        body, body_errors = self._get_body(request, operation)

        errors = params_errors + body_errors
        return RequestValidationResult(errors, body, params)

    def _get_parameters(self, request, params):
        errors = []
        seen = set()
        locations = {}
        for param_name, param in params:
            if (param_name, param.location.value) in seen:
                # skip parameter already seen
                # e.g. overriden path item paremeter on operation
                continue
            seen.add((param_name, param.location.value))
            try:
                raw_value = param.get_raw_value(request)
            except MissingRequiredParameter as exc:
                errors.append(exc)
                continue
            except OpenAPIParameterError:
                continue

            try:
                casted = param.cast(raw_value)
            except OpenAPIParameterError as exc:
                errors.append(exc)
                continue

            try:
                unmarshalled = param.unmarshal(
                    casted, self.custom_formatters,
                    resolver=self.spec._resolver,
                )
            except OpenAPIParameterError as exc:
                errors.append(exc)
            else:
                locations.setdefault(param.location.value, {})
                locations[param.location.value][param_name] = unmarshalled

        return RequestParameters(**locations), errors

    def _get_body(self, request, operation):
        errors = []

        if operation.request_body is None:
            return None, errors

        body = None
        try:
            media_type = operation.request_body[request.mimetype]
        except InvalidContentType as exc:
            errors.append(exc)
        else:
            try:
                raw_body = operation.request_body.get_value(request)
            except MissingRequestBody as exc:
                errors.append(exc)
            else:
                try:
                    casted = media_type.cast(raw_body)
                except InvalidMediaTypeValue as exc:
                    errors.append(exc)
                else:
                    try:
                        body = media_type.unmarshal(
                            casted, self.custom_formatters,
                            resolver=self.spec._resolver,
                        )
                    except InvalidMediaTypeValue as exc:
                        errors.append(exc)

        return body, errors
