"""OpenAPI core paths models module"""


class Path(object):
    """Represents an OpenAPI Path."""

    def __init__(
            self, name, operations,
            summary=None, description=None, parameters=None, servers=None,
            extensions=None,
    ):
        self.name = name
        self.operations = dict(operations)
        self.summary = summary
        self.description = description
        self.servers = servers
        self.parameters = dict(parameters) if parameters else {}

        self.extensions = extensions and dict(extensions) or {}

    def __getitem__(self, http_method):
        return self.operations[http_method]
