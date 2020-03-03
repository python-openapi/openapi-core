"""OpenAPI core servers models module"""
from six import iteritems
from six.moves.urllib.parse import urljoin


class Server(object):

    def __init__(self, url, variables=None, description=None, extensions=None):
        self.url = url
        self.variables = variables and dict(variables) or {}
        self.description = description

        self.extensions = extensions and dict(extensions) or {}

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

    @staticmethod
    def is_absolute(url):
        return url.startswith('//') or '://' in url

    def get_absolute_url(self, base_url=None):
        if base_url is not None and not self.is_absolute(self.url):
            return urljoin(base_url, self.url)
        return self.url


class ServerVariable(object):

    def __init__(self, name, default, enum=None, extensions=None):
        self.name = name
        self.default = default
        self.enum = enum and list(enum) or []

        self.extensions = extensions and dict(extensions) or {}
