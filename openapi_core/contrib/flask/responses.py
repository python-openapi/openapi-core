"""OpenAPI core contrib flask responses module"""
import re

from openapi_core.validation.response.datatypes import OpenAPIResponse


class FlaskOpenAPIResponseFactory(object):

    @classmethod
    def create(cls, response):
        return OpenAPIResponse(
            data=response.data,
            status_code=response._status_code,
            mimetype=response.mimetype,
        )
