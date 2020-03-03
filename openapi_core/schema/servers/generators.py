"""OpenAPI core servers generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.servers.models import Server, ServerVariable


class ServersGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, servers_spec):
        servers_deref = self.dereferencer.dereference(servers_spec)
        for server_spec in servers_deref:
            url = server_spec['url']
            variables_spec = server_spec.get('variables', {})
            description = server_spec.get('description')

            extensions = self.extensions_generator.generate(server_spec)

            variables = None
            if variables_spec:
                variables = self.variables_generator.generate(variables_spec)

            yield Server(
                url,
                variables=variables, description=description,
                extensions=extensions,
            )

    @property
    @lru_cache()
    def variables_generator(self):
        return ServerVariablesGenerator(self.dereferencer)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)


class ServerVariablesGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, variables_spec):
        variables_deref = self.dereferencer.dereference(variables_spec)

        for variable_name, variable_spec in iteritems(variables_deref):
            default = variable_spec['default']
            enum = variable_spec.get('enum')

            extensions = self.extensions_generator.generate(variable_spec)

            variable = ServerVariable(
                variable_name, default,
                enum=enum, extensions=extensions,
            )
            yield variable_name, variable

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
