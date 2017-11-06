"""OpenAPI core exceptions module"""


class OpenAPIError(Exception):
    pass


class OpenAPIMappingError(OpenAPIError):
    pass


class OpenAPIServerError(OpenAPIMappingError):
    pass


class OpenAPIOperationError(OpenAPIMappingError):
    pass


class InvalidValueType(OpenAPIMappingError):
    pass


class OpenAPIParameterError(OpenAPIMappingError):
    pass


class OpenAPIBodyError(OpenAPIMappingError):
    pass


class InvalidServer(OpenAPIServerError):
    pass


class InvalidOperation(OpenAPIOperationError):
    pass


class EmptyValue(OpenAPIParameterError):
    pass


class MissingParameter(OpenAPIParameterError):
    pass


class InvalidParameterValue(OpenAPIParameterError):
    pass


class MissingBody(OpenAPIBodyError):
    pass


class InvalidMediaTypeValue(OpenAPIBodyError):
    pass


class UndefinedSchemaProperty(OpenAPIBodyError):
    pass


class MissingProperty(OpenAPIBodyError):
    pass


class InvalidContentType(OpenAPIBodyError):
    pass


class InvalidResponse(OpenAPIMappingError):
    pass


class InvalidValue(OpenAPIMappingError):
    pass
