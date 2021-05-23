"""OpenAPI core contrib falcon responses module"""
from werkzeug.datastructures import Headers

from openapi_core.contrib.falcon.compat import get_response_text
from openapi_core.validation.response.datatypes import OpenAPIResponse


class FalconOpenAPIResponseFactory:
    @classmethod
    def create(cls, response):
        resp_mimetype: str = ''
        if response.content_type:
            resp_mimetype = response.content_type.partition(";")[0]
        else:
            resp_mimetype = response.options.default_media_type
        resp_status_code: int = int(response.status[:3])
        resp_data: str = get_response_text(response)
        resp_headers: Headers = Headers(response.headers)
        return OpenAPIResponse(
            data=resp_data,
            status_code=resp_status_code,
            headers=resp_headers,
            mimetype=resp_mimetype,
        )
