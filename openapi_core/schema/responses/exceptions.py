import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIResponseError(OpenAPIMappingError):
    pass


@attr.s(hash=True)
class MissingResponseContent(OpenAPIResponseError):
    response = attr.ib()

    def __str__(self):
        return "Missing response content"
