"""OpenAPI core paths module"""
from functools import lru_cache

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

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, paths):
        paths_deref = self.dereferencer.dereference(paths)
        for path_name, path in iteritems(paths_deref):
            operations = self.operations_generator.generate(path_name, path)
            yield path_name, Path(path_name, list(operations))

    @property
    @lru_cache()
    def operations_generator(self):
        return OperationsGenerator(self.dereferencer, self.schemas_registry)
