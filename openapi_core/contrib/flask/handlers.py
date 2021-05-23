"""OpenAPI core contrib flask handlers module"""
from typing import Sequence

from flask import Response
from flask.globals import current_app
from flask.json import dumps

from openapi_core.contrib.flask.types import FlaskOpenAPIError
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import (
    ServerNotFound, OperationNotFound, PathNotFound,
)
from openapi_core.validation.types import ValidationErrors


class FlaskOpenAPIErrorsHandler:

    OPENAPI_ERROR_STATUS = {
        ServerNotFound: 400,
        OperationNotFound: 405,
        PathNotFound: 404,
        MediaTypeNotFound: 415,
    }

    @classmethod
    def handle(cls, errors: Sequence[ValidationErrors]) -> Response:
        data_errors = [
            cls.format_openapi_error(err)
            for err in errors
        ]
        data = {
            'errors': data_errors,
        }
        data_error_max = max(data_errors, key=cls.get_error_status)
        status = data_error_max['status']
        response: Response = current_app.response_class(
            dumps(data),
            status=status,
            mimetype='application/json'
        )
        return response

    @classmethod
    def format_openapi_error(cls, error: ValidationErrors) -> FlaskOpenAPIError:
        return FlaskOpenAPIError(
            name=str(type(error)),
            message=str(error),
            status=cls.OPENAPI_ERROR_STATUS.get(error.__class__, 400),
        )

    @classmethod
    def get_error_status(cls, error: FlaskOpenAPIError) -> int:
        return error['status']
