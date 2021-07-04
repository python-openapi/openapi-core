"""OpenAPI core contrib requests responses module"""
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse


class RequestsOpenAPIResponseFactory:
    @classmethod
    def create(cls, response):
        mimetype = response.headers.get("Content-Type")
        headers = Headers(dict(response.headers))
        return OpenAPIResponse(
            data=response.content,
            status_code=response.status_code,
            headers=headers,
            mimetype=mimetype,
        )
