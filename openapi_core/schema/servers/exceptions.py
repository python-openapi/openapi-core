import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIServerError(OpenAPIMappingError):
    pass


@attr.s(hash=True)
class InvalidServer(OpenAPIServerError):
    full_url_pattern = attr.ib()

    def __str__(self):
        return "Invalid request server {0}".format(
            self.full_url_pattern)
