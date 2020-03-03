class Components(object):
    """Represents an OpenAPI Components in a service."""

    def __init__(
            self, schemas=None, responses=None, parameters=None,
            request_bodies=None, security_schemes=None, extensions=None):
        self.schemas = schemas and dict(schemas) or {}
        self.responses = responses and dict(responses) or {}
        self.parameters = parameters and dict(parameters) or {}
        self.request_bodies = request_bodies and dict(request_bodies) or {}
        self.security_schemes = (
            security_schemes and dict(security_schemes) or {}
        )

        self.extensions = extensions and dict(extensions) or {}
