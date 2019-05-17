"""OpenAPI core paths generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.operations.generators import OperationsGenerator
from openapi_core.schema.parameters.generators import ParametersGenerator
from openapi_core.schema.paths.models import Path


class PathsGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, paths):
        paths_deref = self.dereferencer.dereference(paths)
        for path_name, path in iteritems(paths_deref):
            operations = self.operations_generator.generate(path_name, path)
            parameters = self.parameters_generator.generate_from_list(
                path.get('parameters', {})
            )
            yield path_name, Path(path_name, list(operations), parameters)

    @property
    @lru_cache()
    def operations_generator(self):
        return OperationsGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def parameters_generator(self):
        return ParametersGenerator(self.dereferencer, self.schemas_registry)
