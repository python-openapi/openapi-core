"""OpenAPI core paths models module"""


class Path(object):
    """Represents an OpenAPI Path."""

    def __init__(self, name, operations):
        self.name = name
        self.operations = dict(operations)

    def __getitem__(self, http_method):
        return self.operations[http_method]
