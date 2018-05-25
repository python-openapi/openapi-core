from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIMediaTypeError(OpenAPIMappingError):
    pass


class InvalidMediaTypeValue(OpenAPIMediaTypeError):
    pass


class InvalidContentType(OpenAPIMediaTypeError):
    pass
