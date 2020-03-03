"""OpenAPI core external docs models module"""


class ExternalDocumentation(object):
    """Represents an OpenAPI External Documentation."""

    def __init__(self, url, description=None, extensions=None):
        self.url = url
        self.description = description

        self.extensions = extensions and dict(extensions) or {}
