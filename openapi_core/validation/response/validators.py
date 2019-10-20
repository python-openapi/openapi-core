"""OpenAPI core validation response validators module"""
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.media_types.exceptions import (
    InvalidMediaTypeValue, InvalidContentType,
)
from openapi_core.schema.responses.exceptions import (
    InvalidResponse, MissingResponseContent,
)
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.util import get_operation_pattern


class ResponseValidator(object):

    def __init__(self, spec, custom_formatters=None):
        self.spec = spec
        self.custom_formatters = custom_formatters

    def validate(self, request, response):
        try:
            server = self.spec.get_server(request.full_url_pattern)
        # don't process if server errors
        except InvalidServer as exc:
            return ResponseValidationResult([exc, ], None, None)

        operation_pattern = get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

        try:
            operation = self.spec.get_operation(
                operation_pattern, request.method)
        # don't process if operation errors
        except InvalidOperation as exc:
            return ResponseValidationResult([exc, ], None, None)

        try:
            operation_response = operation.get_response(
                str(response.status_code))
        # don't process if operation response errors
        except InvalidResponse as exc:
            return ResponseValidationResult([exc, ], None, None)

        data, data_errors = self._get_data(response, operation_response)

        headers, headers_errors = self._get_headers(
            response, operation_response)

        errors = data_errors + headers_errors
        return ResponseValidationResult(errors, data, headers)

    def _get_data(self, response, operation_response):
        errors = []

        if not operation_response.content:
            return None, errors

        data = None
        try:
            media_type = operation_response[response.mimetype]
        except InvalidContentType as exc:
            errors.append(exc)
        else:
            try:
                raw_data = operation_response.get_value(response)
            except MissingResponseContent as exc:
                errors.append(exc)
            else:
                try:
                    casted = media_type.cast(raw_data)
                except InvalidMediaTypeValue as exc:
                    errors.append(exc)
                else:
                    try:
                        data = media_type.unmarshal(
                            casted, self.custom_formatters,
                            resolver=self.spec._resolver,
                        )
                    except InvalidMediaTypeValue as exc:
                        errors.append(exc)

        return data, errors

    def _get_headers(self, response, operation_response):
        errors = []

        # @todo: implement
        headers = {}

        return headers, errors
