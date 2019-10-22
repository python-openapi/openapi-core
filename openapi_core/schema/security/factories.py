"""OpenAPI core security factories module"""
from openapi_core.schema.security.models import SecurityRequirement


class SecurityRequirementFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, security_requirement_spec):
        name = next(iter(security_requirement_spec))
        scope_names = security_requirement_spec[name]

        return SecurityRequirement(name, scope_names=scope_names)
