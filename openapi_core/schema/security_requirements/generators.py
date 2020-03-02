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
            yield SecurityRequirement(security_requirement_spec)
