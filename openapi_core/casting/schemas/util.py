"""OpenAPI core casting schemas util module"""
from typing import Union

from distutils.util import strtobool


def forcebool(val: Union[str, int]) -> bool:
    if isinstance(val, str):
        val = strtobool(val)

    return bool(val)
