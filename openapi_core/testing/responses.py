"""OpenAPI core testing responses module"""
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse


class MockResponseFactory:

    @classmethod
    def create(
            cls, data, status_code=200, headers=None,
            mimetype='application/json'):
        resp_headers: Headers = Headers(headers or {})
        return OpenAPIResponse(
            data=data,
            status_code=status_code,
            headers=resp_headers,
            mimetype=mimetype,
        )
