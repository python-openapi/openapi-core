from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


@dataclass
class CastError(OpenAPIError):
    """Schema cast operation error"""
    value: str
    type: str

    def __str__(self):
        return "Failed to cast value {value} to type {type}".format(
            value=self.value, type=self.type)
