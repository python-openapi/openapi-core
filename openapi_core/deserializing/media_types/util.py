from email.parser import BytesParser
from json import loads

from six import binary_type
from six.moves.urllib.parse import parse_qsl


def json_loads(value):
    # python 3.5 doesn't support binary input fix
    if isinstance(value, (binary_type, )):
        value = value.decode()
    return loads(value)


def urlencoded_form_loads(value):
    return dict(parse_qsl(value))


def data_form_loads(value):
    if issubclass(type(value), str):
        value = value.encode()
    parser = BytesParser()
    parts = parser.parsebytes(value)
    return dict(
        (
            part.get_param('name', header='content-disposition'),
            part.get_payload(decode=True),
        )
        for part in parts.get_payload()
    )
