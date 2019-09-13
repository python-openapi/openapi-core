import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPISchemaError(OpenAPIMappingError):
    pass


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
class InvalidCustomFormatSchemaValue(InvalidSchemaValue):
    original_exception = attr.ib()

    def __str__(self):
        return self.msg.format(value=self.value, type=self.type, exception=self.original_exception)


@attr.s(hash=True)
class UndefinedSchemaProperty(OpenAPISchemaError):
    extra_props = attr.ib()

    def __str__(self):
        return "Extra unexpected properties found in schema: {0}".format(self.extra_props)


@attr.s(hash=True)
class InvalidSchemaProperty(OpenAPISchemaError):
    property_name = attr.ib()
    original_exception = attr.ib()

    def __str__(self):
        return "Invalid schema property {0}: {1}".format(self.property_name, self.original_exception)


@attr.s(hash=True)
class MissingSchemaProperty(OpenAPISchemaError):
    property_name = attr.ib()

    def __str__(self):
        return "Missing schema property: {0}".format(self.property_name)


class UnmarshallerError(OpenAPIMappingError):
    pass


class UnmarshallerStrictTypeError(UnmarshallerError):
    value = attr.ib()
    types = attr.ib()
    
    def __str__(self):
        return "Value {value} is not one of types {types}".format(
            self.value, self.types)
