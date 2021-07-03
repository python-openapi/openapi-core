"""OpenAPI core contrib flask responses module"""
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse


class FlaskOpenAPIResponseFactory:
    @classmethod
    def create(cls, response):
        header = Headers(response.headers)
        return OpenAPIResponse(
            data=response.data,
            status_code=response._status_code,
            headers=header,
            mimetype=response.mimetype,
        )
