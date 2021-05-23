"""OpenAPI core validation response exceptions module"""
from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.response.datatypes import OpenAPIResponse


class OpenAPIResponseError(OpenAPIError):
    pass


@dataclass
class MissingResponseContent(OpenAPIResponseError):
    response: OpenAPIResponse

    def __str__(self):
        return "Missing response content"
