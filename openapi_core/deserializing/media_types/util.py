from typing import Union

from email.parser import Parser
from urllib.parse import parse_qsl


def urlencoded_form_loads(value: str) -> dict:
    return dict(parse_qsl(value))


def data_form_loads(value: Union[bytes, str]) -> dict:
    if isinstance(value, bytes):
        value = value.decode('ASCII', errors='surrogateescape')
    parser = Parser()
    parts = parser.parsestr(value, headersonly=False)
    return {
        part.get_param('name', header='content-disposition'):
        part.get_payload(decode=True)
        for part in parts.get_payload()
    }
