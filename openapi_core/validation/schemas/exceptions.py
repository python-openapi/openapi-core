from dataclasses import dataclass
from dataclasses import field
from typing import Iterable

from openapi_core.exceptions import OpenAPIError


class ValidateError(OpenAPIError):
    """Schema validate operation error"""


@dataclass
class InvalidSchemaValue(ValidateError):
    """Value not valid for schema"""

    value: str
    type: str
    schema_errors: Iterable[Exception] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            "Value {value} not valid for schema of type {type}: {errors}"
        ).format(value=self.value, type=self.type, errors=self.schema_errors)
