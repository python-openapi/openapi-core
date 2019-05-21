"""OpenAPI core links generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.links.models import Link
from openapi_core.schema.parameters.generators import ParametersGenerator
from openapi_core.schema.servers.generators import ServersGenerator


class LinksGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, links):
        for link_name, link in iteritems(links):
            link_deref = self.dereferencer.dereference(link)
            operation_id = link_deref.get('operationId')
            parameters = link_deref.get('parameters', {})
            request_body = link_deref.get('requestBody')  # string or dict
            description = link_deref.get('description')
            server_spec = link_deref.get('server')
            server = self.servers_generator.generate(server_spec) \
                if server_spec is not None \
                else None

            yield link_name, Link(
                operation_id,
                parameters,
                request_body,
                description,
                server
            )

    @property
    @lru_cache()
    def parameters_generator(self):
        return ParametersGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def servers_generator(self):
        return ServersGenerator(self.dereferencer)
