"""OpenAPI core schemas util module"""
from distutils.util import strtobool


def forcebool(val):
    if isinstance(val, str):
        val = strtobool(val)

    return bool(val)
