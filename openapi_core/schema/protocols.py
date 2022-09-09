from typing import TYPE_CHECKING
from typing import Any
from typing import List

if TYPE_CHECKING:
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable
else:
    try:
        from typing import Protocol
        from typing import runtime_checkable
    except ImportError:
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
