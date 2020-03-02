import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIParameterError(OpenAPIMappingError):
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
