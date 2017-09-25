from functools import lru_cache

from six import iteritems


class Server(object):

    def __init__(self, url, variables=None):
        self.url = url
        self.variables = variables and dict(variables) or {}

    @property
    def default_url(self):
        return self.get_url()

    @property
    def default_variables(self):
        defaults = {}
        for name, variable in iteritems(self.variables):
            defaults[name] = variable.default
        return defaults

    def get_url(self, **variables):
        if not variables:
            variables = self.default_variables
        return self.url.format(**variables)


class ServerVariable(object):

    def __init__(self, name, default, enum=None):
        self.name = name
        self.default = default
        self.enum = enum and list(enum) or []


class ServersGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, servers_spec):
        servers_deref = self.dereferencer.dereference(servers_spec)
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

        if not variables_deref:
            return [Server('/'), ]

        for variable_name, variable_spec in iteritems(variables_deref):
            default = variable_spec['default']
            enum = variable_spec.get('enum')

            variable = ServerVariable(variable_name, default, enum=enum)
            yield variable_name, variable
