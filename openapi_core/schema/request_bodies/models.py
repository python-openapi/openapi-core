"""OpenAPI core request bodies models module"""
from openapi_core.exceptions import InvalidContentType


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
