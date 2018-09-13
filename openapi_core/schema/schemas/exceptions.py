from openapi_core.schema.exceptions import OpenAPIMappingError

import attr


class OpenAPISchemaError(OpenAPIMappingError):
    pass


@attr.s
class NoValidSchema(OpenAPISchemaError):
    value = attr.ib()

    def __str__(self):
        return "No valid schema found for value: {0}".format(self.value)


@attr.s
class UndefinedItemsSchema(OpenAPISchemaError):
    type = attr.ib()

    def __str__(self):
        return "Null value for schema type {0}".format(self.type)


@attr.s
class InvalidSchemaValue(OpenAPISchemaError):
    msg = attr.ib()
    value = attr.ib()
    type = attr.ib()

    def __str__(self):
        return self.msg.format(value=self.value, type=self.type)

@attr.s
class InvalidCustomFormatSchemaValue(InvalidSchemaValue):
    original_exception = attr.ib()

    def __str__(self):
        return self.msg.format(value=self.value, type=self.type, exception=self.original_exception)


@attr.s
class UndefinedSchemaProperty(OpenAPISchemaError):
    extra_props = attr.ib()

    def __str__(self):
        return "Extra unexpected properties found in schema: {0}".format(self.extra_props)

@attr.s
class InvalidSchemaProperty(OpenAPISchemaError):
    property_name = attr.ib()
    original_exception = attr.ib()

    def __str__(self):
        return "Invalid schema property {0}: {1}".format(self.property_name, self.original_exception)

@attr.s
class MissingSchemaProperty(OpenAPISchemaError):
    property_name = attr.ib()

    def __str__(self):
        return "Missing schema property: {0}".format(self.property_name)


@attr.s
class NoOneOfSchema(OpenAPISchemaError):
    type = attr.ib()

    def __str__(self):
        return "Exactly one valid schema type {0} should be valid, None found.".format(self.type)


@attr.s
class MultipleOneOfSchema(OpenAPISchemaError):
    type = attr.ib()

    def __str__(self):
        return "Exactly one schema type {0} should be valid, more than one found".format(self.type)
