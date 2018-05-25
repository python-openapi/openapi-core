"""OpenAPI core servers models module"""
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
