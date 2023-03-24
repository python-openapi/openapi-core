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
from openapi_core.templating.paths.iterators import SimpleOperationsIterator
from openapi_core.templating.paths.iterators import SimplePathsIterator
from openapi_core.templating.paths.iterators import SimpleServersIterator
from openapi_core.templating.paths.iterators import TemplatePathsIterator
from openapi_core.templating.paths.iterators import TemplateServersIterator
from openapi_core.templating.paths.protocols import OperationsIterator
from openapi_core.templating.paths.protocols import PathsIterator
from openapi_core.templating.paths.protocols import ServersIterator
from openapi_core.templating.paths.util import template_path_len
from openapi_core.templating.util import parse
from openapi_core.templating.util import search


class PathFinder:
    paths_iterator: PathsIterator = NotImplemented
    operations_iterator: OperationsIterator = NotImplemented
    servers_iterator: ServersIterator = NotImplemented

    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        self.spec = spec
        self.base_url = base_url

    def find(self, method: str, name: str) -> PathOperationServer:
        paths_iter = self.paths_iterator(
            name,
            self.spec,
            base_url=self.base_url,
        )
        paths_iter_peek = peekable(paths_iter)

        if not paths_iter_peek:
            raise PathNotFound(name)

        operations_iter = self.operations_iterator(
            method,
            paths_iter_peek,
            self.spec,
            base_url=self.base_url,
        )
        operations_iter_peek = peekable(operations_iter)

        if not operations_iter_peek:
            raise OperationNotFound(name, method)

        servers_iter = self.servers_iterator(
            name, operations_iter_peek, self.spec, base_url=self.base_url
        )

        try:
            return next(servers_iter)
        except StopIteration:
            raise ServerNotFound(name)


class APICallPathFinder(PathFinder):
    paths_iterator: PathsIterator = TemplatePathsIterator("paths")
    operations_iterator: OperationsIterator = SimpleOperationsIterator()
    servers_iterator: ServersIterator = TemplateServersIterator()


class WebhookPathFinder(APICallPathFinder):
    paths_iterator = SimplePathsIterator("webhooks")
    servers_iterator = SimpleServersIterator()
