from typing import Iterator
from typing import List
from typing import Optional
from urllib.parse import urljoin
from urllib.parse import urlparse

from jsonschema_path import SchemaPath

from openapi_core.schema.servers import is_absolute
from openapi_core.templating.datatypes import TemplateResult
from openapi_core.templating.paths.datatypes import Path
from openapi_core.templating.paths.datatypes import PathOperation
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.templating.paths.exceptions import PathsNotFound
from openapi_core.templating.paths.util import template_path_len
from openapi_core.templating.util import parse
from openapi_core.templating.util import search


class SimplePathsIterator:
    def __init__(self, paths_part: str):
        self.paths_part = paths_part

    def __call__(
        self, name: str, spec: SchemaPath, base_url: Optional[str] = None
    ) -> Iterator[Path]:
        paths = spec / self.paths_part
        if not paths.exists():
            raise PathsNotFound(paths.as_uri())
        for path_name, path in list(paths.items()):
            if name == path_name:
                path_result = TemplateResult(path_name, {})
                yield Path(path, path_result)


class TemplatePathsIterator:
    def __init__(self, paths_part: str):
        self.paths_part = paths_part

    def __call__(
        self, name: str, spec: SchemaPath, base_url: Optional[str] = None
    ) -> Iterator[Path]:
        paths = spec / self.paths_part
        if not paths.exists():
            raise PathsNotFound(paths.as_uri())
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


class SimpleOperationsIterator:
    def __call__(
        self,
        method: str,
        paths_iter: Iterator[Path],
        spec: SchemaPath,
        base_url: Optional[str] = None,
    ) -> Iterator[PathOperation]:
        for path, path_result in paths_iter:
            if method not in path:
                continue
            operation = path / method
            yield PathOperation(path, operation, path_result)


class CatchAllMethodOperationsIterator(SimpleOperationsIterator):
    def __init__(self, ca_method_name: str, ca_operation_name: str):
        self.ca_method_name = ca_method_name
        self.ca_operation_name = ca_operation_name

    def __call__(
        self,
        method: str,
        paths_iter: Iterator[Path],
        spec: SchemaPath,
        base_url: Optional[str] = None,
    ) -> Iterator[PathOperation]:
        if method == self.ca_method_name:
            yield from super().__call__(
                self.ca_operation_name, paths_iter, spec, base_url=base_url
            )
        else:
            yield from super().__call__(
                method, paths_iter, spec, base_url=base_url
            )


class SimpleServersIterator:
    def __call__(
        self,
        name: str,
        operations_iter: Iterator[PathOperation],
        spec: SchemaPath,
        base_url: Optional[str] = None,
    ) -> Iterator[PathOperationServer]:
        for path, operation, path_result in operations_iter:
            yield PathOperationServer(
                path,
                operation,
                None,
                path_result,
                {},
            )


class TemplateServersIterator:
    def __call__(
        self,
        name: str,
        operations_iter: Iterator[PathOperation],
        spec: SchemaPath,
        base_url: Optional[str] = None,
    ) -> Iterator[PathOperationServer]:
        for path, operation, path_result in operations_iter:
            servers = (
                path.get("servers", None)
                or operation.get("servers", None)
                or spec.get("servers", None)
            )
            if not servers:
                servers = [SchemaPath.from_dict({"url": "/"})]
            for server in servers:
                server_url_pattern = name.rsplit(path_result.resolved, 1)[0]
                server_url = server["url"]
                if not is_absolute(server_url):
                    # relative to absolute url
                    if base_url is not None:
                        server_url = urljoin(base_url, server["url"])
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
                    # servers should'n end with tailing slash
                    # but let's search for this too
                    server_url_pattern += "/"
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
