"""OpenAPI core exceptions module"""


class OpenAPIError(Exception):
    pass


class OpenAPIMappingError(OpenAPIError):
    pass


class MissingParameterError(OpenAPIMappingError):
    pass


class MissingPropertyError(OpenAPIMappingError):
    pass


class InvalidContentTypeError(OpenAPIMappingError):
    pass


class InvalidServerError(OpenAPIMappingError):
    pass


class InvalidValueType(OpenAPIMappingError):
    pass


class UndefinedSchemaProperty(OpenAPIMappingError):
    pass
