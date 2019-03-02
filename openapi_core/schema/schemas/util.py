"""OpenAPI core schemas util module"""
import datetime
from distutils.util import strtobool
from json import dumps
from six import string_types, text_type
import strict_rfc3339


def forcebool(val):
    if isinstance(val, string_types):
        val = strtobool(val)

    return bool(val)


def strictbool(val):
    if not isinstance(val, bool):
        raise TypeError('expected bool, got {type}'.format(type=type(val)))
    return val


def strictstr(val):
    if not isinstance(val, text_type):
        raise TypeError('expected text, got {type}'.format(type=type(val)))
    return val

def dicthash(d):
    return hash(dumps(d, sort_keys=True))


def format_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


def format_datetime(value):
    timestamp = strict_rfc3339.rfc3339_to_timestamp(value)
    return datetime.datetime.utcfromtimestamp(timestamp)
