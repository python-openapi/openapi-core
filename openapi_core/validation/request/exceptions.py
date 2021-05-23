"""OpenAPI core validation request exceptions module"""
from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.request.datatypes import OpenAPIRequest


class OpenAPIRequestBodyError(OpenAPIError):
    pass


class MissingRequestBodyError(OpenAPIRequestBodyError):
    """Missing request body error"""
    pass


@dataclass
class MissingRequestBody(MissingRequestBodyError):
    request: OpenAPIRequest

    def __str__(self):
        return "Missing request body"


@dataclass
class MissingRequiredRequestBody(MissingRequestBodyError):
    request: OpenAPIRequest

    def __str__(self):
        return "Missing required request body"
