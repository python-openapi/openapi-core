"""OpenAPI core schemas util module"""
from base64 import b64decode
import datetime
from distutils.util import strtobool
from six import string_types, text_type, integer_types
from uuid import UUID


def forcebool(val):
    if isinstance(val, string_types):
        val = strtobool(val)

    return bool(val)


def format_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


def format_uuid(value):
    if isinstance(value, UUID):
        return value
    return UUID(value)


def format_byte(value, encoding='utf8'):
    return text_type(b64decode(value), encoding)


def format_number(value):
    if isinstance(value, integer_types + (float, )):
        return value

    return float(value)
