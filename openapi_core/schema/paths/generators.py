"""OpenAPI core paths generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.operations.generators import OperationsGenerator
from openapi_core.schema.paths.models import Path


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
