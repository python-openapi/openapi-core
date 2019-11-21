"""OpenAPI core contrib falcon responses module"""
from openapi_core.validation.response.datatypes import OpenAPIResponse


class FalconOpenAPIResponseFactory(object):
    @classmethod
    def create(cls, resp):
        return OpenAPIResponse(
            data=resp.body,
            status_code=resp.status[:3],
            mimetype=resp.content_type.partition(";")[0] if resp.content_type else '',
        )
