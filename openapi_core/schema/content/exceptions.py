import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIContentError(OpenAPIMappingError):
    pass


@attr.s(hash=True)
class MimeTypeNotFound(OpenAPIContentError):
    mimetype = attr.ib()
    availableMimetypes = attr.ib()

    def __str__(self):
        return "Mimetype not found: {0}. Valid mimetypes: {1}".format(self.mimetype, self.availableMimetypes)
