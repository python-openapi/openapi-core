"""OpenAPI core validation exceptions module"""
from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


class ValidationError(OpenAPIError):
    pass


@dataclass
class InvalidSecurity(ValidationError):
    def __str__(self):
        return "Security not valid for any requirement"
