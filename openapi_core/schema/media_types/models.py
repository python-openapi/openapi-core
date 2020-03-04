"""OpenAPI core media types models module"""


class MediaType(object):
    """Represents an OpenAPI MediaType."""

    def __init__(self, mimetype, schema=None, example=None, extensions=None):
        self.mimetype = mimetype
        self.schema = schema
        self.example = example

        self.extensions = extensions and dict(extensions) or {}
