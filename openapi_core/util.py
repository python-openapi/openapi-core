"""OpenAPI core util module"""

from itertools import chain
from typing import Any
from typing import Iterable

BOOLEAN_TRUE_VALUES = ("y", "yes", "t", "true", "on", "1")
BOOLEAN_FALSE_VALUES = ("n", "no", "f", "false", "off", "0")


def forcebool(val: Any) -> bool:
    if isinstance(val, str):
        val = val.lower()
        if val in BOOLEAN_TRUE_VALUES:
            return True
        elif val in BOOLEAN_FALSE_VALUES:
            return False
        else:
            raise ValueError(f"invalid truth value {val!r}")

    return bool(val)


def chainiters(*lists: Iterable[Any]) -> Iterable[Any]:
    iters = map(lambda l: l and iter(l) or [], lists)
    return chain(*iters)
