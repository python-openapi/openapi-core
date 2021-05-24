"""OpenAPI core contrib django responses module"""
from openapi_core.contrib.django.compat import get_response_headers
from openapi_core.validation.response.datatypes import OpenAPIResponse


class DjangoOpenAPIResponseFactory:

    @classmethod
    def create(cls, response):
        mimetype = response["Content-Type"]
        headers = get_response_headers(response)
        return OpenAPIResponse(
            data=response.content,
            status_code=response.status_code,
            headers=list(headers.items()),
            mimetype=mimetype,
        )
