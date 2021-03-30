"""OpenAPI core request bodies models module"""


class RequestBody(object):
    """Represents an OpenAPI RequestBody."""

    def __init__(self, content, required=False, extensions=None):
        self.content = content
        self.required = required

        self.extensions = extensions and dict(extensions) or {}
