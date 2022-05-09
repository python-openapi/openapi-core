"""OpenAPI core schemas util module"""
import datetime
from base64 import b64decode
from copy import copy
from functools import lru_cache
from uuid import UUID

from openapi_schema_validator import oas30_format_checker


def format_date(value):
    return datetime.datetime.strptime(value, "%Y-%m-%d").date()


def format_uuid(value):
    if isinstance(value, UUID):
        return value
    return UUID(value)


def format_byte(value, encoding="utf8"):
    return str(b64decode(value), encoding)


def format_number(value):
    if isinstance(value, (int, float)):
        return value

    return float(value)


@lru_cache()
def build_format_checker(**custom_formatters):
    if not custom_formatters:
        return oas30_format_checker

    fc = copy(oas30_format_checker)
    for name, formatter in list(custom_formatters.items()):
        fc.checks(name)(formatter.validate)
    return fc
