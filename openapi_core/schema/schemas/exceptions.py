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


class UnmarshalError(OpenAPISchemaError):
    """Schema unmarshal operation error"""
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
class InvalidSchemaValue(ValidateError):
    value = attr.ib()
    type = attr.ib()
    _schema_errors = attr.ib(default=None)
    _schema_errors_iter = attr.ib(factory=list)

    @property
    def schema_errors(self):
        if self._schema_errors is None:
            self._schema_errors = list(self._schema_errors_iter)
        return self._schema_errors

    def __str__(self):
        return (
            "Value {value} not valid for schema of type {type}: {errors}"
        ).format(value=self.value, type=self.type, errors=self.schema_errors)


class UnmarshallerError(UnmarshalError):
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
