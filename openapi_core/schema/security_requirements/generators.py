"""OpenAPI core security requirements generators module"""
from openapi_core.schema.security_requirements.models import (
    SecurityRequirement,
)


class SecurityRequirementsGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, security_spec):
        security_deref = self.dereferencer.dereference(security_spec)
        for security_requirement_spec in security_deref:
            name = next(iter(security_requirement_spec))
            scope_names = security_requirement_spec[name]

            yield SecurityRequirement(name, scope_names=scope_names)
