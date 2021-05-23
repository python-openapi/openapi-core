"""OpenAPI core contrib requests responses module"""
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse


class RequestsOpenAPIResponseFactory:

    @classmethod
    def create(cls, response):
        resp_headers: Headers = Headers(dict(response.headers))
        resp_mimetype: str = response.headers.get('Content-Type')
        return OpenAPIResponse(
            data=response.content,
            status_code=response.status_code,
            headers=resp_headers,
            mimetype=resp_mimetype,
        )
