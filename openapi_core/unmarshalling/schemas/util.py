"""OpenAPI core schemas util module"""
from base64 import b64decode
from copy import deepcopy
from datetime import date
from datetime import datetime
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Optional
from typing import Union
from uuid import UUID

from jsonschema._format import FormatChecker
from openapi_schema_validator import oas30_format_checker


def format_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_uuid(value: Any) -> UUID:
    if isinstance(value, UUID):
        return value
    return UUID(value)


def format_byte(value: str, encoding: str = "utf8") -> str:
    return str(b64decode(value), encoding)


def format_number(value: str) -> Union[int, float]:
    if isinstance(value, (int, float)):
        return value

    return float(value)


@lru_cache()
def build_format_checker(
    format_checker: Optional[FormatChecker] = None,
    **format_checks: Callable[[Any], bool]
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
