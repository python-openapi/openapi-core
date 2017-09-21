"""OpenAPI core paths module"""
from six import iteritems

from openapi_core.operations import OperationsGenerator


class Path(object):
    """Represents an OpenAPI Path."""

    def __init__(self, name, operations):
        self.name = name
        self.operations = dict(operations)

    def __getitem__(self, http_method):
        return self.operations[http_method]


class PathsGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, paths):
        paths_deref = self.dereferencer.dereference(paths)
        for path_name, path in iteritems(paths_deref):
            operations = self._generate_operations(path_name, path)
            yield path_name, Path(path_name, list(operations))

    def _generate_operations(self, path_name, path):
        return OperationsGenerator(self.dereferencer).generate(path_name, path)
