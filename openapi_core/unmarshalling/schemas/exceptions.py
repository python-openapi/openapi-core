from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


class UnmarshalError(OpenAPIError):
    """Schema unmarshal operation error"""


class UnmarshallerError(UnmarshalError):
    """Unmarshaller error"""


@dataclass
class FormatterNotFoundError(UnmarshallerError):
    """Formatter not found to unmarshal"""

    type_format: str

    def __str__(self) -> str:
        return f"Formatter not found for {self.type_format} format"


@dataclass
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
