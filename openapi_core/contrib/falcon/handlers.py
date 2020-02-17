"""OpenAPI core contrib falcon handlers module"""
from json import dumps

from falcon.constants import MEDIA_JSON
from falcon.status_codes import (
    HTTP_400, HTTP_404, HTTP_405, HTTP_415,
)
from openapi_core.schema.media_types.exceptions import InvalidContentType
from openapi_core.templating.paths.exceptions import (
    ServerNotFound, OperationNotFound, PathNotFound,
)


class FalconOpenAPIErrorsHandler(object):

    OPENAPI_ERROR_STATUS = {
        ServerNotFound: 400,
        OperationNotFound: 405,
        PathNotFound: 404,
        InvalidContentType: 415,
    }

    FALCON_STATUS_CODES = {
        400: HTTP_400,
        404: HTTP_404,
        405: HTTP_405,
        415: HTTP_415,
    }

    @classmethod
    def handle(cls, req, resp, errors):
        data_errors = [
            cls.format_openapi_error(err)
            for err in errors
        ]
        data = {
            'errors': data_errors,
        }
        data_error_max = max(data_errors, key=lambda x: x['status'])
        resp.content_type = MEDIA_JSON
        resp.status = cls.FALCON_STATUS_CODES.get(
            data_error_max['status'], HTTP_400)
        resp.body = dumps(data)
        resp.complete = True

    @classmethod
    def format_openapi_error(cls, error):
        return {
            'title': str(error),
            'status': cls.OPENAPI_ERROR_STATUS.get(error.__class__, 400),
            'class': str(type(error)),
        }
