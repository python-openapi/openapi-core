"""OpenAPI core exceptions module"""
from dataclasses import dataclass


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
    pass


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
