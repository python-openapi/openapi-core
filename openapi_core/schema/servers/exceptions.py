from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIServerError(OpenAPIMappingError):
    pass


class InvalidServer(OpenAPIServerError):
    pass
