"""OpenAPI core validation exceptions module"""
from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


@dataclass
class ValidationError(OpenAPIError):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.__cause__}"
