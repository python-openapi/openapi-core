from openapi_core.schema.exceptions import OpenAPIMappingError

import attr


class OpenAPIMediaTypeError(OpenAPIMappingError):
    pass

@attr.s
class InvalidMediaTypeValue(OpenAPIMediaTypeError):
    original_exception = attr.ib()

    def __str__(self):
        return "Mimetype invalid: {0}".format(self.original_exception)

@attr.s
class InvalidContentType(OpenAPIMediaTypeError):
    mimetype = attr.ib()

    def __str__(self):
        return "Content for following mimetype not found: {0}".format(self.mimetype)
