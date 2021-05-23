"""OpenAPI core contrib flask responses module"""
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse


class FlaskOpenAPIResponseFactory:

    @classmethod
    def create(cls, response):
        resp_headers: Headers = Headers(response.headers)
        return OpenAPIResponse(
            data=response.data,
            status_code=response._status_code,
            headers=resp_headers,
            mimetype=response.mimetype,
        )
