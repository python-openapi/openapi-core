from six import text_type, binary_type, integer_types

from openapi_core.schema.schemas.enums import SchemaFormat, SchemaType
from openapi_core.schema.schemas.exceptions import (
    InvalidSchemaValue, InvalidCustomFormatSchemaValue,
    OpenAPISchemaError,
    InvalidSchemaProperty,
    UnmarshallerStrictTypeError,
)
from openapi_core.schema.schemas.util import (
    forcebool, format_date, format_datetime, format_byte, format_uuid,
    format_number,
)


class StrictUnmarshaller(object):

    STRICT_TYPES = ()

    def __call__(self, value, type_format=SchemaFormat.NONE, strict=True):
        if self.STRICT_TYPES and strict and not isinstance(
                value, self.STRICT_TYPES):
            raise UnmarshallerStrictTypeError(value, self.STRICT_TYPES)

        return value


class PrimitiveTypeUnmarshaller(StrictUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: lambda x: x,
    }

    def __init__(self, custom_formatters=None):
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters

    def __call__(self, value, type_format=SchemaFormat.NONE, strict=True):
        value = super(PrimitiveTypeUnmarshaller, self).__call__(
            value, type_format=type_format, strict=strict)

        try:
            schema_format = SchemaFormat(type_format)
        except ValueError:
            formatter = self.custom_formatters.get(type_format)
        else:
            formatters = self.get_formatters()
            formatter = formatters.get(schema_format)

        if formatter is None:
            raise InvalidSchemaValue(
                "Unsupported format {type} unmarshalling "
                "for value {value}",
                value, type_format)

        try:
            return formatter(value)
        except ValueError as exc:
            raise InvalidCustomFormatSchemaValue(
                "Failed to format value {value} to format {type}: {exception}",
                value, type_format, exc)

    def get_formatters(self):
        return self.FORMATTERS


class StringUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = (text_type, binary_type)
    FORMATTERS = {
        SchemaFormat.NONE: text_type,
        SchemaFormat.PASSWORD: text_type,
        SchemaFormat.DATE: format_date,
        SchemaFormat.DATETIME: format_datetime,
        SchemaFormat.BINARY: binary_type,
        SchemaFormat.UUID: format_uuid,
        SchemaFormat.BYTE: format_byte,
    }


class IntegerUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = integer_types
    FORMATTERS = {
        SchemaFormat.NONE: int,
        SchemaFormat.INT32: int,
        SchemaFormat.INT64: int,
    }


class NumberUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = (float, ) + integer_types
    FORMATTERS = {
        SchemaFormat.NONE: format_number,
        SchemaFormat.FLOAT: float,
        SchemaFormat.DOUBLE: float,
    }


class BooleanUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = (bool, )
    FORMATTERS = {
        SchemaFormat.NONE: forcebool,
    }
