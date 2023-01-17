import sys
from typing import Any
from typing import List

if sys.version_info >= (3, 8):
    from typing import Protocol
    from typing import runtime_checkable
else:
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable


@runtime_checkable
class SuportsGetAll(Protocol):
    def getall(self, name: str) -> List[Any]:
        ...


@runtime_checkable
class SuportsGetList(Protocol):
    def getlist(self, name: str) -> List[Any]:
        ...
