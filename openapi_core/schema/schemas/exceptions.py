import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPISchemaError(OpenAPIMappingError):
    pass


class UnmarshallError(OpenAPISchemaError):
    """Unmarshall operation error"""
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
class NoValidSchema(OpenAPISchemaError):
    value = attr.ib()

    def __str__(self):
        return "No valid schema found for value: {0}".format(self.value)


@attr.s(hash=True)
class UndefinedItemsSchema(OpenAPISchemaError):
    type = attr.ib()

    def __str__(self):
        return "Null value for schema type {0}".format(self.type)


@attr.s(hash=True)
class InvalidSchemaValue(OpenAPISchemaError):
    msg = attr.ib()
    value = attr.ib()
    type = attr.ib()

    def __str__(self):
        return self.msg.format(value=self.value, type=self.type)


@attr.s(hash=True)
class UndefinedSchemaProperty(OpenAPISchemaError):
    extra_props = attr.ib()

    def __str__(self):
        return "Extra unexpected properties found in schema: {0}".format(
            self.extra_props)


@attr.s(hash=True)
class InvalidSchemaProperty(OpenAPISchemaError):
    property_name = attr.ib()
    original_exception = attr.ib()

    def __str__(self):
        return "Invalid schema property {0}: {1}".format(
            self.property_name, self.original_exception)


@attr.s(hash=True)
class MissingSchemaProperty(OpenAPISchemaError):
    property_name = attr.ib()

    def __str__(self):
        return "Missing schema property: {0}".format(self.property_name)


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
