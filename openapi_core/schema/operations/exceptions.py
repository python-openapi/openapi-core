from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIOperationError(OpenAPIMappingError):
    pass


class InvalidOperation(OpenAPIOperationError):
    pass
