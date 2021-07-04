"""OpenAPI core contrib falcon responses module"""
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse


class FalconOpenAPIResponseFactory:
    @classmethod
    def create(cls, response):
        status_code = int(response.status[:3])

        mimetype = ""
        if response.content_type:
            mimetype = response.content_type.partition(";")[0]
        else:
            mimetype = response.options.default_media_type

        data = response.text
        headers = Headers(response.headers)

        return OpenAPIResponse(
            data=data,
            status_code=status_code,
            headers=headers,
            mimetype=mimetype,
        )
