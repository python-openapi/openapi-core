class Components(object):
    """Represents an OpenAPI Components in a service."""

    def __init__(
            self, schemas=None, responses=None, parameters=None,
            request_bodies=None):
        self.schemas = schemas and dict(schemas) or {}
        self.responses = responses and dict(responses) or {}
        self.parameters = parameters and dict(parameters) or {}
        self.request_bodies = request_bodies and dict(request_bodies) or {}
