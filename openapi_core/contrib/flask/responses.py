"""OpenAPI core contrib flask responses module"""
from flask import Response
from werkzeug.datastructures import Headers

from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.factories import (
    BaseOpenAPIResponseFactory,
)


class FlaskOpenAPIResponseFactory(BaseOpenAPIResponseFactory):

    @classmethod
    def create(cls, response: Response) -> OpenAPIResponse:
        resp_headers: Headers = Headers(response.headers)
        return OpenAPIResponse(
            data=response.data,
            status_code=response._status_code,
            headers=resp_headers,
            mimetype=response.mimetype,
        )
