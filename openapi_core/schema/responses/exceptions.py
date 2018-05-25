from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIResponseError(OpenAPIMappingError):
    pass


class InvalidResponse(OpenAPIResponseError):
    pass


class MissingResponseContent(OpenAPIResponseError):
    pass
