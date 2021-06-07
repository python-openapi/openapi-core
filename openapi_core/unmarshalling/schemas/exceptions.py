from typing import List

from dataclasses import dataclass, field

from openapi_core.exceptions import OpenAPIError


class UnmarshalError(OpenAPIError):
    """Schema unmarshal operation error"""
    pass


class ValidateError(UnmarshalError):
    """Schema validate operation error"""
    pass


class UnmarshallerError(UnmarshalError):
    """Unmarshaller error"""
    pass


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
            value=self.value, type=self.type,
            exception=self.original_exception,
        )


@dataclass
class FormatterNotFoundError(UnmarshallerError):
    """Formatter not found to unmarshal"""
    type_format: str

    def __str__(self):
        return "Formatter not found for {format} format".format(
            format=self.type_format)
