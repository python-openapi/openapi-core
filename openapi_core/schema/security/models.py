"""OpenAPI core security models module"""


class SecurityRequirement(object):
    """Represents an OpenAPI Security Requirement."""

    def __init__(self, name, scope_names=None):
        self.name = name
        self.scope_names = scope_names or []
