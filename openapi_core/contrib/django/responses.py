"""OpenAPI core contrib django responses module"""
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse


class DjangoOpenAPIResponseFactory:
    def create(self, response):
        return OpenAPIResponse(
            data=self._get_data(response),
            status_code=self._get_status_code(response),
            headers=self._get_header(response),
            mimetype=self._get_mimetype(response),
        )

    def _get_data(self, response):
        return response.content

    def _get_status_code(self, response):
        return response.status_code

    def _get_header(self, response):
        return Headers(response.headers.items())

    def _get_mimetype(self, response):
        return response["Content-Type"]
