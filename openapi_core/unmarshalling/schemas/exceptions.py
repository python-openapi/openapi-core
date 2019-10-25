import attr

from openapi_core.exceptions import OpenAPIError


class UnmarshalError(OpenAPIError):
    """Schema unmarshal operation error"""
    pass


class UnmarshallerError(UnmarshalError):
    """Unmarshaller error"""
    pass


@attr.s(hash=True)
class UnmarshalValueError(UnmarshalError):
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
    type_format = attr.ib()

    def __str__(self):
        return "Formatter not found for {format} format".format(
            format=self.type_format)


@attr.s(hash=True)
class UnmarshallerStrictTypeError(UnmarshallerError):
    value = attr.ib()
    types = attr.ib()

    def __str__(self):
        types = ', '.join(list(map(str, self.types)))
        return "Value {value} is not one of types: {types}".format(
            value=self.value, types=types)
