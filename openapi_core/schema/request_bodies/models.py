"""OpenAPI core request bodies models module"""
from openapi_core.schema.content.exceptions import MimeTypeNotFound
from openapi_core.schema.content.models import Content
from openapi_core.schema.media_types.exceptions import InvalidContentType


class RequestBody(object):
    """Represents an OpenAPI RequestBody."""

    def __init__(self, content, required=False, extensions=None):
        self.content = Content(content)
        self.required = required

        self.extensions = extensions and dict(extensions) or {}

    def __getitem__(self, mimetype):
        try:
            return self.content[mimetype]
        except MimeTypeNotFound:
            raise InvalidContentType(mimetype)
