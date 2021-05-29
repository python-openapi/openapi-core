"""OpenAPI core contrib django responses module"""
from werkzeug.datastructures import Headers

from openapi_core.contrib.django.compat import get_response_headers
from openapi_core.validation.response.datatypes import OpenAPIResponse


class DjangoOpenAPIResponseFactory:

    @classmethod
    def create(cls, response):
        mimetype = response["Content-Type"]
        headers = get_response_headers(response)
        header = Headers(headers.items())
        return OpenAPIResponse(
            data=response.content,
            status_code=response.status_code,
            headers=header,
            mimetype=mimetype,
        )
