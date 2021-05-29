from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


@dataclass
class DeserializeError(OpenAPIError):
    """Deserialize operation error"""
    value: str
    style: str

    def __str__(self):
        return "Failed to deserialize value {value} with style {style}".format(
            value=self.value, style=self.style)
