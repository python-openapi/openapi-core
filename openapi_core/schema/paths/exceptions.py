import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIPathError(OpenAPIMappingError):
    pass


@attr.s(hash=True)
class InvalidPath(OpenAPIPathError):
    path_pattern = attr.ib()

    def __str__(self):
        return "Unknown path {0}".format(self.path_pattern)
