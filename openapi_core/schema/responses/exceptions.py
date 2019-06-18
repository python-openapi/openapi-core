import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIResponseError(OpenAPIMappingError):
    pass


@attr.s(hash=True)
class InvalidResponse(OpenAPIResponseError):
    http_status = attr.ib()
    responses = attr.ib()

    def __str__(self):
        return "Unknown response http status: {0}".format(str(self.http_status))


@attr.s(hash=True)
class MissingResponseContent(OpenAPIResponseError):
    response = attr.ib()

    def __str__(self):
        return "Missing response content"
