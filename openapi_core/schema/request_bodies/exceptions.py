from openapi_core.schema.exceptions import OpenAPIMappingError

import attr


class OpenAPIRequestBodyError(OpenAPIMappingError):
    pass


@attr.s
class MissingRequestBody(OpenAPIRequestBodyError):
    request = attr.ib()

    def __str__(self):
        return "Missing required request body"
