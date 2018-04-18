from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIParameterError(OpenAPIMappingError):
    pass


class MissingParameter(OpenAPIParameterError):
    pass


class MissingRequiredParameter(OpenAPIParameterError):
    pass


class EmptyParameterValue(OpenAPIParameterError):
    pass


class InvalidParameterValue(OpenAPIParameterError):
    pass
