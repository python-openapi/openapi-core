"""OpenAPI core templating paths finders module"""
from typing import Generator, Optional, Tuple
from urllib.parse import urljoin, urlparse

from more_itertools import peekable

from openapi_core.schema.servers import is_absolute
from openapi_core.spec.paths import SpecPath
from openapi_core.templating.datatypes import TemplateResult
from openapi_core.templating.util import parse, search
from openapi_core.templating.paths.datatypes import (
    PathResult, OperationResult, ServerResult,
)
from openapi_core.templating.paths.exceptions import (
    PathNotFound, OperationNotFound, ServerNotFound,
)
from openapi_core.templating.paths.util import template_path_len


class PathFinder:

    def __init__(self, spec: SpecPath, base_url: Optional[str] = None):
        self.spec = spec
        self.base_url = base_url

    def find(self, request) -> ServerResult:
        paths_iter = self._get_paths_iter(request.full_url_pattern)
        paths_iter_peek = peekable(paths_iter)

        if not paths_iter_peek:
            raise PathNotFound(request.full_url_pattern)

        operations_iter = self._get_operations_iter(
            request.method, paths_iter_peek)
        operations_iter_peek = peekable(operations_iter)

        if not operations_iter_peek:
            raise OperationNotFound(request.full_url_pattern, request.method)

        servers_iter = self._get_servers_iter(
            request.full_url_pattern, operations_iter_peek)

        try:
            return next(servers_iter)
        except StopIteration:
            raise ServerNotFound(request.full_url_pattern)

    def _get_paths_iter(
        self,
        full_url_pattern: str,
    ) -> Generator[PathResult, None, None]:
        template_paths = []
        paths = self.spec / 'paths'
        for path_pattern, path in list(paths.items()):
            # simple path.
            # Return right away since it is always the most concrete
            if full_url_pattern.endswith(path_pattern):
                path_template = TemplateResult(path_pattern)
                yield PathResult(path, path_template)
            # template path
            else:
                result = search(path_pattern, full_url_pattern)
                if result:
                    path_template = TemplateResult(path_pattern, result.named)
                    template_paths.append((path, path_template))

        # Fewer variables -> more concrete path
        for path in sorted(template_paths, key=template_path_len):
            yield PathResult(*path)

    def _get_operations_iter(
        self,
        request_method: str,
        paths_iter: peekable,
    ) -> Generator[OperationResult, None, None]:
        for path, path_template in paths_iter:
            if request_method not in path:
                continue
            operation = path / request_method
            yield OperationResult(path, operation, path_template)

    def _get_servers_iter(
        self,
        full_url_pattern: str,
        ooperations_iter: peekable,
    ) -> Generator[ServerResult, None, None]:
        for path, operation, path_template in ooperations_iter:
            servers = path.get('servers', None) or \
                operation.get('servers', None) or \
                self.spec.get('servers', [{'url': '/'}])
            for server in servers:
                server_url_pattern = full_url_pattern.rsplit(
                    path_template.resolved, 1)[0]
                server_url = server['url']
                if not is_absolute(server_url):
                    # relative to absolute url
                    if self.base_url is not None:
                        server_url = urljoin(self.base_url, server['url'])
                    # if no base url check only path part
                    else:
                        server_url_pattern = urlparse(server_url_pattern).path
                if server_url.endswith('/'):
                    server_url = server_url[:-1]
                # simple path
                if server_url_pattern == server_url:
                    server_template = TemplateResult(server['url'])
                    yield ServerResult(
                        path, operation, server,
                        path_template, server_template,
                    )
                # template path
                else:
                    result = parse(server['url'], server_url_pattern)
                    if result:
                        server_template = TemplateResult(
                            server['url'], result.named)
                        yield ServerResult(
                            path, operation, server,
                            path_template, server_template,
                        )
