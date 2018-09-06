from openapi_core.schema.exceptions import OpenAPIMappingError

import attr


class OpenAPIOperationError(OpenAPIMappingError):
    pass


@attr.s
class InvalidOperation(OpenAPIOperationError):
    path_pattern = attr.ib()
    http_method = attr.ib()

    def __str__(self):
        return "Unknown operation path {0} with method {1}".format(
            self.path_pattern, self.http_method)
