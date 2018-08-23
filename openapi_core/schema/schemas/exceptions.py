from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPISchemaError(OpenAPIMappingError):
    pass


class NoValidSchema(OpenAPISchemaError):
    pass


class UndefinedItemsSchema(OpenAPISchemaError):
    pass


class InvalidSchemaValue(OpenAPISchemaError):
    pass


class UndefinedSchemaProperty(OpenAPISchemaError):
    pass


class MissingSchemaProperty(OpenAPISchemaError):
    pass


class NoOneOfSchema(OpenAPISchemaError):
    pass


class MultipleOneOfSchema(OpenAPISchemaError):
    pass
