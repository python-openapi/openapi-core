"""OpenAPI core exceptions module"""
from dataclasses import dataclass

from openapi_core.validation.request.protocols import Request
from openapi_core.validation.response.protocols import Response


class OpenAPIError(Exception):
    pass


class OpenAPIHeaderError(OpenAPIError):
    pass


class MissingHeaderError(OpenAPIHeaderError):
    """Missing header error"""


@dataclass
class MissingHeader(MissingHeaderError):
    name: str

    def __str__(self):
        return f"Missing header (without default value): {self.name}"


@dataclass
class MissingRequiredHeader(MissingHeaderError):
    name: str

    def __str__(self):
        return f"Missing required header: {self.name}"


class OpenAPIParameterError(OpenAPIError):
    pass


class MissingParameterError(OpenAPIParameterError):
    """Missing parameter error"""


@dataclass
class MissingParameter(MissingParameterError):
    name: str

    def __str__(self):
        return f"Missing parameter (without default value): {self.name}"


@dataclass
class MissingRequiredParameter(MissingParameterError):
    name: str

    def __str__(self):
        return f"Missing required parameter: {self.name}"


class OpenAPIRequestBodyError(OpenAPIError):
    pass


class MissingRequestBodyError(OpenAPIRequestBodyError):
    """Missing request body error"""


@dataclass
class MissingRequestBody(MissingRequestBodyError):
    request: Request

    def __str__(self):
        return "Missing request body"


@dataclass
class MissingRequiredRequestBody(MissingRequestBodyError):
    request: Request

    def __str__(self):
        return "Missing required request body"


class OpenAPIResponseError(OpenAPIError):
    pass


@dataclass
class MissingResponseContent(OpenAPIResponseError):
    response: Response

    def __str__(self):
        return "Missing response content"
