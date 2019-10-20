import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPISchemaError(OpenAPIMappingError):
    pass


@attr.s(hash=True)
class CastError(OpenAPISchemaError):
    """Schema cast operation error"""
    value = attr.ib()
    type = attr.ib()

    def __str__(self):
        return "Failed to cast value {value} to type {type}".format(
            value=self.value, type=self.type)


class ValidateError(OpenAPISchemaError):
    """Schema validate operation error"""
    pass


class UnmarshallError(OpenAPISchemaError):
    """Schema unmarshall operation error"""
    pass


@attr.s(hash=True)
class UnmarshallValueError(UnmarshallError):
    """Failed to unmarshal value to type"""
    value = attr.ib()
    type = attr.ib()
    original_exception = attr.ib(default=None)

    def __str__(self):
        return (
            "Failed to unmarshal value {value} to type {type}: {exception}"
        ).format(
            value=self.value, type=self.type,
            exception=self.original_exception,
        )


@attr.s(hash=True)
class InvalidSchemaValue(ValidateError):
    value = attr.ib()
    type = attr.ib()

    def __str__(self):
        return "Value {value} not valid for schema of type {type}".format(
            value=self.value, type=self.type)


class UnmarshallerError(UnmarshallError):
    """Unmarshaller error"""
    pass


@attr.s(hash=True)
class InvalidCustomFormatSchemaValue(UnmarshallerError):
    """Value failed to format with custom formatter"""
    value = attr.ib()
    type = attr.ib()
    original_exception = attr.ib()

    def __str__(self):
        return (
            "Failed to format value {value} to format {type}: {exception}"
        ).format(
            value=self.value, type=self.type,
            exception=self.original_exception,
        )


@attr.s(hash=True)
class FormatterNotFoundError(UnmarshallerError):
    """Formatter not found to unmarshal"""
    value = attr.ib()
    type_format = attr.ib()

    def __str__(self):
        return (
            "Formatter not found for {format} format "
            "to unmarshal value {value}"
        ).format(format=self.type_format, value=self.value)


@attr.s(hash=True)
class UnmarshallerStrictTypeError(UnmarshallerError):
    value = attr.ib()
    types = attr.ib()
    
    def __str__(self):
        types = ', '.join(list(map(str, self.types)))
        return "Value {value} is not one of types: {types}".format(
            value=self.value, types=types)
