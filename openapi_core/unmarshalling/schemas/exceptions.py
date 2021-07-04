from dataclasses import dataclass
from dataclasses import field
from typing import List

from openapi_core.exceptions import OpenAPIError


class UnmarshalError(OpenAPIError):
    """Schema unmarshal operation error"""


class ValidateError(UnmarshalError):
    """Schema validate operation error"""


class UnmarshallerError(UnmarshalError):
    """Unmarshaller error"""


@dataclass
class InvalidSchemaValue(ValidateError):
    value: str
    type: str
    schema_errors: List[Exception] = field(default_factory=list)

    def __str__(self):
        return (
            "Value {value} not valid for schema of type {type}: {errors}"
        ).format(value=self.value, type=self.type, errors=self.schema_errors)


@dataclass
class InvalidSchemaFormatValue(UnmarshallerError):
    """Value failed to format with formatter"""

    value: str
    type: str
    original_exception: Exception

    def __str__(self):
        return (
            "Failed to format value {value} to format {type}: {exception}"
        ).format(
            value=self.value,
            type=self.type,
            exception=self.original_exception,
        )


@dataclass
class FormatterNotFoundError(UnmarshallerError):
    """Formatter not found to unmarshal"""

    type_format: str

    def __str__(self):
        return f"Formatter not found for {self.type_format} format"
