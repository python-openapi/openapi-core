"""OpenAPI core extensions models module"""


class Extension(object):
    """Represents an OpenAPI Extension."""

    def __init__(self, field_name, value=None):
        self.field_name = field_name
        self.value = value
