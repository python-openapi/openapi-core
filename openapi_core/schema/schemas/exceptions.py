from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPISchemaError(OpenAPIMappingError):
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
