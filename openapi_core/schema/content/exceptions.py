from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIContentError(OpenAPIMappingError):
    pass


class MimeTypeNotFound(OpenAPIContentError):
    pass
