from dataclasses import dataclass
from typing import Any

from openapi_core.deserializing.exceptions import DeserializeError


@dataclass
class CastError(DeserializeError):
    """Schema cast operation error"""

    value: Any
    type: str

    def __str__(self) -> str:
        return f"Failed to cast value to {self.type} type: {self.value}"
