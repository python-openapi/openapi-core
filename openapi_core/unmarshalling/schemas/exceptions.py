from dataclasses import dataclass
from dataclasses import field
from typing import Iterable

from openapi_core.exceptions import OpenAPIError


class UnmarshalError(OpenAPIError):
    """Schema unmarshal operation error"""


class ValidateError(UnmarshalError):
    """Schema validate operation error"""


class UnmarshallerError(UnmarshalError):
    """Unmarshaller error"""


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


@dataclass
class InvalidFormatValue(UnmarshallerError):
    """Value not valid for format"""

    value: str
    type: str

    def __str__(self) -> str:
        return ("value {value} not valid for format {type}").format(
            value=self.value,
            type=self.type,
        )


class FormatUnmarshalError(UnmarshallerError):
    """Unable to unmarshal value for format"""

    value: str
    type: str
    original_exception: Exception

    def __str__(self) -> str:
        return (
            "Unable to unmarshal value {value} for format {type}: {exception}"
        ).format(
            value=self.value,
            type=self.type,
            exception=self.original_exception,
        )
