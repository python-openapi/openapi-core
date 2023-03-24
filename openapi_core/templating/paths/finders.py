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
from openapi_core.templating.paths.datatypes import Path
from openapi_core.templating.paths.datatypes import PathOperation
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import PathsNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.paths.util import template_path_len
from openapi_core.templating.util import parse
from openapi_core.templating.util import search


class BasePathFinder:
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        self.spec = spec
        self.base_url = base_url

    def find(self, method: str, name: str) -> PathOperationServer:
        paths_iter = self._get_paths_iter(name)
        paths_iter_peek = peekable(paths_iter)

        if not paths_iter_peek:
            raise PathNotFound(name)

        operations_iter = self._get_operations_iter(method, paths_iter_peek)
        operations_iter_peek = peekable(operations_iter)

        if not operations_iter_peek:
            raise OperationNotFound(name, method)

        servers_iter = self._get_servers_iter(
            name,
            operations_iter_peek,
        )

        try:
            return next(servers_iter)
        except StopIteration:
            raise ServerNotFound(name)

    def _get_paths_iter(self, name: str) -> Iterator[Path]:
        raise NotImplementedError

    def _get_operations_iter(
        self, method: str, paths_iter: Iterator[Path]
    ) -> Iterator[PathOperation]:
        for path, path_result in paths_iter:
            if method not in path:
                continue
            operation = path / method
            yield PathOperation(path, operation, path_result)

    def _get_servers_iter(
        self, name: str, operations_iter: Iterator[PathOperation]
    ) -> Iterator[PathOperationServer]:
        raise NotImplementedError


class APICallPathFinder(BasePathFinder):
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        self.spec = spec
        self.base_url = base_url

    def _get_paths_iter(self, name: str) -> Iterator[Path]:
        paths = self.spec / "paths"
        if not paths.exists():
            raise PathsNotFound(paths.uri())
        template_paths: List[Path] = []
        for path_pattern, path in list(paths.items()):
            # simple path.
            # Return right away since it is always the most concrete
            if name.endswith(path_pattern):
                path_result = TemplateResult(path_pattern, {})
                yield Path(path, path_result)
            # template path
            else:
                result = search(path_pattern, name)
                if result:
                    path_result = TemplateResult(path_pattern, result.named)
                    template_paths.append(Path(path, path_result))

        # Fewer variables -> more concrete path
        yield from sorted(template_paths, key=template_path_len)

    def _get_servers_iter(
        self, name: str, operations_iter: Iterator[PathOperation]
    ) -> Iterator[PathOperationServer]:
        for path, operation, path_result in operations_iter:
            servers = (
                path.get("servers", None)
                or operation.get("servers", None)
                or self.spec.get("servers", [{"url": "/"}])
            )
            for server in servers:
                server_url_pattern = name.rsplit(path_result.resolved, 1)[0]
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
                    yield PathOperationServer(
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
                        yield PathOperationServer(
                            path,
                            operation,
                            server,
                            path_result,
                            server_result,
                        )


class WebhookPathFinder(BasePathFinder):
    def _get_paths_iter(self, name: str) -> Iterator[Path]:
        webhooks = self.spec / "webhooks"
        if not webhooks.exists():
            raise PathsNotFound(webhooks.uri())
        for webhook_name, path in list(webhooks.items()):
            if name == webhook_name:
                path_result = TemplateResult(webhook_name, {})
                yield Path(path, path_result)

    def _get_servers_iter(
        self, name: str, operations_iter: Iterator[PathOperation]
    ) -> Iterator[PathOperationServer]:
        for path, operation, path_result in operations_iter:
            yield PathOperationServer(
                path,
                operation,
                None,
                path_result,
                {},
            )
