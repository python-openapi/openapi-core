from functools import lru_cache

from openapi_core.schemas import SchemasGenerator


class Components(object):
    """Represents an OpenAPI Components in a service."""

    def __init__(
            self, schemas=None, responses=None, parameters=None,
            request_bodies=None):
        self.schemas = schemas and dict(schemas) or {}
        self.responses = responses and dict(responses) or {}
        self.parameters = parameters and dict(parameters) or {}
        self.request_bodies = request_bodies and dict(request_bodies) or {}


class ComponentsFactory(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def create(self, components_spec):
        components_deref = self.dereferencer.dereference(components_spec)

        schemas_spec = components_deref.get('schemas', [])
        responses_spec = components_deref.get('responses', [])
        parameters_spec = components_deref.get('parameters', [])
        request_bodies_spec = components_deref.get('request_bodies', [])

        schemas = self.schemas_generator.generate(schemas_spec)
        responses = self._generate_response(responses_spec)
        parameters = self._generate_parameters(parameters_spec)
        request_bodies = self._generate_request_bodies(request_bodies_spec)
        return Components(
            schemas=list(schemas), responses=responses, parameters=parameters,
            request_bodies=request_bodies,
        )

    @property
    @lru_cache()
    def schemas_generator(self):
        return SchemasGenerator(self.dereferencer, self.schemas_registry)

    def _generate_response(self, responses_spec):
        return responses_spec

    def _generate_parameters(self, parameters_spec):
        return parameters_spec

    def _generate_request_bodies(self, request_bodies_spec):
        return request_bodies_spec
