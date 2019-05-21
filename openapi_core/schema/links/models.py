"""OpenAPI core links models module"""


class Link(object):
    """Represents an OpenAPI Link."""

    def __init__(
            self,
            operation_id,
            parameters,
            request_body,
            description,
            server
    ):
        """
        request_body is assumed to be either a string (JSON, YAML or
        runtime expression) or an object (deserialized JSON or YAML)
        """
        self.operationId = operation_id
        self.description = description
        self.server = server
        self.parameters = dict(parameters) if parameters else {}
        self.request_body = request_body

    def __getitem__(self, item):
        return self.parameters[item]
