from openapi_core.schema.exceptions import OpenAPIMappingError

import attr


class OpenAPIResponseError(OpenAPIMappingError):
    pass


@attr.s
class InvalidResponse(OpenAPIResponseError):
    http_status = attr.ib()
    responses = attr.ib()

    def __str__(self):
        return "Unknown response http status: {0}".format(str(self.http_status))


@attr.s
class MissingResponseContent(OpenAPIResponseError):
    response = attr.ib()

    def __str__(self):
        return "Missing response content"
