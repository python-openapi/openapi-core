"""OpenAPI core templating paths finders module"""
from typing import Iterator
from typing import List
from typing import Optional
from urllib.parse import urljoin
from urllib.parse import urlparse

from more_itertools import peekable

from openapi_core.schema.servers import is_absolute
from openapi_core.spec import Spec
from openapi_core.templating.datatypes import TemplateResult
from openapi_core.templating.paths.datatypes import OperationPath
from openapi_core.templating.paths.datatypes import Path
from openapi_core.templating.paths.datatypes import ServerOperationPath
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.paths.util import template_path_len
from openapi_core.templating.util import parse
from openapi_core.templating.util import search


class PathFinder:
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        self.spec = spec
        self.base_url = base_url

    def find(
        self,
        method: str,
        host_url: str,
        path: str,
        path_pattern: Optional[str] = None,
    ) -> ServerOperationPath:
        if path_pattern is not None:
            full_url = urljoin(host_url, path_pattern)
        else:
            full_url = urljoin(host_url, path)

        paths_iter = self._get_paths_iter(full_url)
        paths_iter_peek = peekable(paths_iter)

        if not paths_iter_peek:
            raise PathNotFound(full_url)

        operations_iter = self._get_operations_iter(paths_iter_peek, method)
        operations_iter_peek = peekable(operations_iter)

        if not operations_iter_peek:
            raise OperationNotFound(full_url, method)

        servers_iter = self._get_servers_iter(
            operations_iter_peek,
            full_url,
        )

        try:
            return next(servers_iter)
        except StopIteration:
            raise ServerNotFound(full_url)

    def _get_paths_iter(self, full_url: str) -> Iterator[Path]:
        template_paths: List[Path] = []
        paths = self.spec / "paths"
        for path_pattern, path in list(paths.items()):
            # simple path.
            # Return right away since it is always the most concrete
            if full_url.endswith(path_pattern):
                path_result = TemplateResult(path_pattern, {})
                yield Path(path, path_result)
            # template path
            else:
                result = search(path_pattern, full_url)
                if result:
                    path_result = TemplateResult(path_pattern, result.named)
                    template_paths.append(Path(path, path_result))

        # Fewer variables -> more concrete path
        yield from sorted(template_paths, key=template_path_len)

    def _get_operations_iter(
        self, paths_iter: Iterator[Path], request_method: str
    ) -> Iterator[OperationPath]:
        for path, path_result in paths_iter:
            if request_method not in path:
                continue
            operation = path / request_method
            yield OperationPath(path, operation, path_result)

    def _get_servers_iter(
        self, operations_iter: Iterator[OperationPath], full_url: str
    ) -> Iterator[ServerOperationPath]:
        for path, operation, path_result in operations_iter:
            servers = (
                path.get("servers", None)
                or operation.get("servers", None)
                or self.spec.get("servers", [{"url": "/"}])
            )
            for server in servers:
                server_url_pattern = full_url.rsplit(path_result.resolved, 1)[
                    0
                ]
                server_url = server["url"]
                if not is_absolute(server_url):
                    # relative to absolute url
                    if self.base_url is not None:
                        server_url = urljoin(self.base_url, server["url"])
                    # if no base url check only path part
                    else:
                        server_url_pattern = urlparse(server_url_pattern).path
                if server_url.endswith("/"):
                    server_url = server_url[:-1]
                # simple path
                if server_url_pattern == server_url:
                    server_result = TemplateResult(server["url"], {})
                    yield ServerOperationPath(
                        path,
                        operation,
                        server,
                        path_result,
                        server_result,
                    )
                # template path
                else:
                    result = parse(server["url"], server_url_pattern)
                    if result:
                        server_result = TemplateResult(
                            server["url"], result.named
                        )
                        yield ServerOperationPath(
                            path,
                            operation,
                            server,
                            path_result,
                            server_result,
                        )
