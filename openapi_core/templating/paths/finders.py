"""OpenAPI core templating paths finders module"""
from openapi_core.templating.paths.util import get_operation_pattern


class PathFinder(object):

    def __init__(self, spec):
        self.spec = spec

    def find(self, request):
        operation_pattern = self._get_operation_pattern(request)

        path = self.spec[operation_pattern]
        path_variables = {}
        operation = self.spec.get_operation(operation_pattern, request.method)
        servers = path.servers or operation.servers or self.spec.servers
        server = servers[0]
        server_variables = {}

        return path, operation, server, path_variables, server_variables

    def _get_operation_pattern(self, request):
        server = self.spec.get_server(request.full_url_pattern)

        return get_operation_pattern(
            server.default_url, request.full_url_pattern
        )
