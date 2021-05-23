"""OpenAPI core contrib django responses module"""
from werkzeug.datastructures import Headers

from openapi_core.contrib.django.compat import get_response_headers
from openapi_core.validation.response.datatypes import OpenAPIResponse


class DjangoOpenAPIResponseFactory:

    @classmethod
    def create(cls, response):
        headers = get_response_headers(response)
        resp_headers: Headers = Headers(headers.items())
        resp_mimetype: str = response["Content-Type"]
        return OpenAPIResponse(
            data=response.content,
            status_code=response.status_code,
            headers=resp_headers,
            mimetype=resp_mimetype,
        )
