"""OpenAPI core schemas util module"""

from base64 import b64decode
from datetime import date
from datetime import datetime
from typing import Any
from typing import Union
from uuid import UUID


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
