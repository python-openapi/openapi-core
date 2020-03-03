"""OpenAPI core paths generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.operations.generators import OperationsGenerator
from openapi_core.schema.parameters.generators import ParametersGenerator
from openapi_core.schema.paths.models import Path
from openapi_core.schema.servers.generators import ServersGenerator


class PathsGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, paths):
        paths_deref = self.dereferencer.dereference(paths)
        for path_name, path_spec in iteritems(paths_deref):
            path_deref = self.dereferencer.dereference(path_spec)

            parameters_list = path_deref.get('parameters', [])
            summary = path_deref.get('summary')
            description = path_deref.get('description')
            servers_spec = path_deref.get('servers', [])

            operations = self.operations_generator.generate(
                path_name, path_deref)
            servers = self.servers_generator.generate(servers_spec)
            parameters = self.parameters_generator.generate_from_list(
                parameters_list)
            extensions = self.extensions_generator.generate(path_deref)

            yield (
                path_name,
                Path(
                    path_name, list(operations), parameters=list(parameters),
                    summary=summary, description=description,
                    servers=list(servers), extensions=extensions,
                ),
            )

    @property
    @lru_cache()
    def operations_generator(self):
        return OperationsGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def servers_generator(self):
        return ServersGenerator(self.dereferencer)

    @property
    @lru_cache()
    def parameters_generator(self):
        return ParametersGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
