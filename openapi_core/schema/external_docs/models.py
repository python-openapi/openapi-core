"""OpenAPI core external docs models module"""


class ExternalDocumentation(object):
    """Represents an OpenAPI External Documentation."""

    def __init__(self, url, description=None):
        self.url = url
        self.description = description
