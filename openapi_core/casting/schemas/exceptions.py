from dataclasses import dataclass
from typing import Any

from openapi_core.exceptions import OpenAPIError


@dataclass
class CastError(OpenAPIError):
    """Schema cast operation error"""

    value: Any
    type: str

    def __str__(self) -> str:
        return f"Failed to cast value to {self.type} type: {self.value}"
