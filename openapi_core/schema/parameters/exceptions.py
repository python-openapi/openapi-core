import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIParameterError(OpenAPIMappingError):
    pass


@attr.s(hash=True)
class MissingParameter(OpenAPIParameterError):
    name = attr.ib()

    def __str__(self):
        return "Missing parameter (without default value): {0}".format(self.name)


@attr.s(hash=True)
class MissingRequiredParameter(OpenAPIParameterError):
    name = attr.ib()

    def __str__(self):
        return "Missing required parameter: {0}".format(self.name)


@attr.s(hash=True)
class EmptyParameterValue(OpenAPIParameterError):
    name = attr.ib()

    def __str__(self):
        return "Value of parameter cannot be empty: {0}".format(self.name)


@attr.s(hash=True)
class InvalidParameterValue(OpenAPIParameterError):
    name = attr.ib()
    original_exception = attr.ib()

    def __str__(self):
        return "Invalid parameter value for `{0}`: {1}".format(self.name, self.original_exception)
