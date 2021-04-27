"""OpenAPI core exceptions module"""
import attr


class OpenAPIError(Exception):
    pass


class OpenAPIMediaTypeError(OpenAPIError):
    pass


@attr.s(hash=True)
class InvalidContentType(OpenAPIMediaTypeError):
    mimetype = attr.ib()

    def __str__(self):
        return "Content for following mimetype not found: {0}".format(
            self.mimetype)


class OpenAPIParameterError(OpenAPIError):
    pass


class MissingParameterError(OpenAPIParameterError):
    """Missing parameter error"""
    pass


@attr.s(hash=True)
class MissingParameter(MissingParameterError):
    name = attr.ib()

    def __str__(self):
        return "Missing parameter (without default value): {0}".format(
            self.name)


@attr.s(hash=True)
class MissingRequiredParameter(MissingParameterError):
    name = attr.ib()

    def __str__(self):
        return "Missing required parameter: {0}".format(self.name)


class OpenAPIRequestBodyError(OpenAPIError):
    pass


@attr.s(hash=True)
class MissingRequestBody(OpenAPIRequestBodyError):
    request = attr.ib()

    def __str__(self):
        return "Missing required request body"


class OpenAPIResponseError(OpenAPIError):
    pass


@attr.s(hash=True)
class MissingResponseContent(OpenAPIResponseError):
    response = attr.ib()

    def __str__(self):
        return "Missing response content"


class OpenAPISchemaError(OpenAPIError):
    pass
