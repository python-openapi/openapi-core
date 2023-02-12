"""OpenAPI core validation schemas util module"""
from copy import deepcopy
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Optional

from jsonschema._format import FormatChecker


@lru_cache()
def build_format_checker(
    format_checker: Optional[FormatChecker] = None,
    **format_checks: Callable[[Any], Any],
) -> Any:
    if format_checker is None:
        fc = FormatChecker()
    else:
        if not format_checks:
            return format_checker
        fc = deepcopy(format_checker)

    for name, check in format_checks.items():
        if name in fc.checkers:
            continue
        fc.checks(name)(check)
    return fc
