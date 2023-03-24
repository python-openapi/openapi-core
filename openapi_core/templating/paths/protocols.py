import sys
from typing import Iterator
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Protocol
    from typing import runtime_checkable
else:
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable

from openapi_core.spec import Spec
from openapi_core.templating.paths.datatypes import Path
from openapi_core.templating.paths.datatypes import PathOperation
from openapi_core.templating.paths.datatypes import PathOperationServer


@runtime_checkable
class PathsIterator(Protocol):
    def __call__(
        self, name: str, spec: Spec, base_url: Optional[str] = None
    ) -> Iterator[Path]:
        ...


@runtime_checkable
class OperationsIterator(Protocol):
    def __call__(
        self,
        method: str,
        paths_iter: Iterator[Path],
        spec: Spec,
        base_url: Optional[str] = None,
    ) -> Iterator[PathOperation]:
        ...


@runtime_checkable
class ServersIterator(Protocol):
    def __call__(
        self,
        name: str,
        operations_iter: Iterator[PathOperation],
        spec: Spec,
        base_url: Optional[str] = None,
    ) -> Iterator[PathOperationServer]:
        ...
