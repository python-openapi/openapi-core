"""OpenAPI core schemas util module"""
import datetime
from json import dumps
from six import string_types, text_type
import strict_rfc3339


def strictbool(val):
    if not isinstance(val, bool):
        raise TypeError('expected bool, got {type}'.format(type=type(val)))
    return val


def strictstr(val):
    if not isinstance(val, string_types):
        raise TypeError('expected text, got {type}'.format(type=type(val)))
    return text_type(val)


def dicthash(d):
    return hash(dumps(d, sort_keys=True))


def format_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


def format_datetime(value):
    timestamp = strict_rfc3339.rfc3339_to_timestamp(value)
    return datetime.datetime.utcfromtimestamp(timestamp)
