from json import loads

from six import binary_type


def json_loads(value):
    # python 3.5 doesn't support binary input fix
    if isinstance(value, (binary_type, )):
        value = value.decode()
    return loads(value)
