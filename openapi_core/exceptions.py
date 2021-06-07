"""OpenAPI core exceptions module"""
from dataclasses import dataclass

from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.response.datatypes import OpenAPIResponse


class OpenAPIError(Exception):
    pass


class OpenAPIHeaderError(OpenAPIError):
    pass


class MissingHeaderError(OpenAPIHeaderError):
    """Missing header error"""
    pass


@dataclass
class MissingHeader(MissingHeaderError):
    name: str

    def __str__(self):
        return "Missing header (without default value): {0}".format(
            self.name)


@dataclass
class MissingRequiredHeader(MissingHeaderError):
    name: str

    def __str__(self):
        return "Missing required header: {0}".format(self.name)


class OpenAPIParameterError(OpenAPIError):
    pass


class MissingParameterError(OpenAPIParameterError):
    """Missing parameter error"""
    pass


@dataclass
class MissingParameter(MissingParameterError):
    name: str

    def __str__(self):
        return "Missing parameter (without default value): {0}".format(
            self.name)


@dataclass
class MissingRequiredParameter(MissingParameterError):
    name: str

    def __str__(self):
        return "Missing required parameter: {0}".format(self.name)


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


class OpenAPIResponseError(OpenAPIError):
    pass


@dataclass
class MissingResponseContent(OpenAPIResponseError):
    response: OpenAPIResponse

    def __str__(self):
        return "Missing response content"
