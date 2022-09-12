"""OpenAPI core validation exceptions module"""
from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


class ValidatorDetectError(OpenAPIError):
    pass


class ValidationError(OpenAPIError):
    pass


@dataclass
class InvalidSecurity(ValidationError):
    def __str__(self) -> str:
        return "Security not valid for any requirement"


class OpenAPIParameterError(OpenAPIError):
    pass


class MissingParameterError(OpenAPIParameterError):
    """Missing parameter error"""


@dataclass
class MissingParameter(MissingParameterError):
    name: str

    def __str__(self) -> str:
        return f"Missing parameter (without default value): {self.name}"


@dataclass
class MissingRequiredParameter(MissingParameterError):
    name: str

    def __str__(self) -> str:
        return f"Missing required parameter: {self.name}"


class OpenAPIHeaderError(OpenAPIError):
    pass


class MissingHeaderError(OpenAPIHeaderError):
    """Missing header error"""


@dataclass
class MissingHeader(MissingHeaderError):
    name: str

    def __str__(self) -> str:
        return f"Missing header (without default value): {self.name}"


@dataclass
class MissingRequiredHeader(MissingHeaderError):
    name: str

    def __str__(self) -> str:
        return f"Missing required header: {self.name}"
