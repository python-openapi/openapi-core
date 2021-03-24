from json import loads

from six import binary_type
from six.moves.urllib.parse import parse_qsl


def json_loads(value):
    # python 3.5 doesn't support binary input fix
    if isinstance(value, (binary_type, )):
        value = value.decode()
    return loads(value)


def form_loads(value):
    return dict(parse_qsl(value))
