"""OpenAPI core request bodies models module"""

from openapi_core.schema.media_types.exceptions import InvalidContentType
from openapi_core.schema.request_bodies.exceptions import MissingRequestBody


class RequestBody(object):
    """Represents an OpenAPI RequestBody."""

    def __init__(self, content, required=False):
        self.content = dict(content)
        self.required = required

    def __getitem__(self, mimetype):
        try:
            return self.content[mimetype]
        except KeyError:
            raise InvalidContentType(
                "Invalid mime type `{0}`".format(mimetype))

    def get_value(self, request):
        if not request.body and self.required:
            raise MissingRequestBody("Missing required request body")

        return request.body
