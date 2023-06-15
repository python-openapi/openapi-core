from typing import Any
from typing import List
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class SuportsGetAll(Protocol):
    def getall(self, name: str) -> List[Any]:
        ...


@runtime_checkable
class SuportsGetList(Protocol):
    def getlist(self, name: str) -> List[Any]:
        ...
