from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIRequestBodyError(OpenAPIMappingError):
    pass


class MissingRequestBody(OpenAPIRequestBodyError):
    pass
