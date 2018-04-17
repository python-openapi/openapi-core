"""OpenAPI core validation response validators module"""
from openapi_core.exceptions import (
    OpenAPIMappingError, MissingBody, InvalidResponse,
)
from openapi_core.validation.response.models import ResponseValidationResult
from openapi_core.validation.util import get_operation_pattern


class ResponseValidator(object):

    def __init__(self, spec):
        self.spec = spec

    def validate(self, request, response):
        errors = []
        data = None
        headers = {}

        try:
            server = self.spec.get_server(request.full_url_pattern)
        # don't process if server errors
        except OpenAPIMappingError as exc:
            errors.append(exc)
            return ResponseValidationResult(errors, data, headers)

        operation_pattern = get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

        try:
            operation = self.spec.get_operation(
                operation_pattern, request.method)
        # don't process if operation errors
        except OpenAPIMappingError as exc:
            errors.append(exc)
            return ResponseValidationResult(errors, data, headers)

        try:
            operation_response = operation.get_response(
                str(response.status_code))
        # don't process if invalid response status code
        except InvalidResponse as exc:
            errors.append(exc)
            return ResponseValidationResult(errors, data, headers)

        if operation_response.content:
            try:
                media_type = operation_response[response.mimetype]
            except OpenAPIMappingError as exc:
                errors.append(exc)
            else:
                try:
                    raw_data = self._get_raw_data(response)
                except MissingBody as exc:
                    errors.append(exc)
                else:
                    try:
                        data = media_type.unmarshal(raw_data)
                    except OpenAPIMappingError as exc:
                        errors.append(exc)

        return ResponseValidationResult(errors, data, headers)

    def _get_raw_data(self, response):
        if not response.data:
            raise MissingBody("Missing required response data")

        return response.data
