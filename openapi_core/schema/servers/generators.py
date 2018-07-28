"""OpenAPI core servers generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.servers.models import Server, ServerVariable


class ServersGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, servers_spec):
        servers_deref = self.dereferencer.dereference(servers_spec)
        if not servers_deref:
            yield Server('/')
            return
        for server_spec in servers_deref:
            url = server_spec['url']
            variables_spec = server_spec.get('variables', {})

            variables = None
            if variables_spec:
                variables = self.variables_generator.generate(variables_spec)

            yield Server(url, variables=variables)

    @property
    @lru_cache()
    def variables_generator(self):
        return ServerVariablesGenerator(self.dereferencer)


class ServerVariablesGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, variables_spec):
        variables_deref = self.dereferencer.dereference(variables_spec)

        for variable_name, variable_spec in iteritems(variables_deref):
            default = variable_spec['default']
            enum = variable_spec.get('enum')

            variable = ServerVariable(variable_name, default, enum=enum)
            yield variable_name, variable
