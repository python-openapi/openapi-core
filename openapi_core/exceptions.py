"""OpenAPI core exceptions module"""


class OpenAPIError(Exception):
    pass


class OpenAPIMappingError(OpenAPIError):
    pass


class MissingParameterError(OpenAPIMappingError):
    pass


class InvalidContentTypeError(OpenAPIMappingError):
    pass
