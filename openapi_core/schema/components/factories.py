from openapi_core.compat import lru_cache
from openapi_core.schema.components.models import Components
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.schemas.generators import SchemasGenerator
from openapi_core.schema.security_schemes.generators import (
    SecuritySchemesGenerator,
)


class ComponentsFactory(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def create(self, components_spec):
        components_deref = self.dereferencer.dereference(components_spec)

        schemas_spec = components_deref.get('schemas', {})
        responses_spec = components_deref.get('responses', {})
        parameters_spec = components_deref.get('parameters', {})
        request_bodies_spec = components_deref.get('requestBodies', {})
        security_schemes_spec = components_deref.get('securitySchemes', {})

        extensions = self.extensions_generator.generate(components_deref)

        schemas = self.schemas_generator.generate(schemas_spec)
        responses = self._generate_response(responses_spec)
        parameters = self._generate_parameters(parameters_spec)
        request_bodies = self._generate_request_bodies(request_bodies_spec)
        security_schemes = self._generate_security_schemes(
            security_schemes_spec)
        return Components(
            schemas=list(schemas), responses=responses, parameters=parameters,
            request_bodies=request_bodies, security_schemes=security_schemes,
            extensions=extensions,
        )

    @property
    @lru_cache()
    def schemas_generator(self):
        return SchemasGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)

    def _generate_response(self, responses_spec):
        return responses_spec

    def _generate_parameters(self, parameters_spec):
        return parameters_spec

    def _generate_request_bodies(self, request_bodies_spec):
        return request_bodies_spec

    def _generate_security_schemes(self, security_schemes_spec):
        return SecuritySchemesGenerator(self.dereferencer).generate(
            security_schemes_spec)
