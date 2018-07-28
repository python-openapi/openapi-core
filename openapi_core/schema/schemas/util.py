"""OpenAPI core schemas util module"""
from distutils.util import strtobool
from json import dumps


def forcebool(val):
    if isinstance(val, str):
        val = strtobool(val)

    return bool(val)


def dicthash(d):
    return hash(dumps(d, sort_keys=True))
