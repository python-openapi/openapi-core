from email.message import Message
from email.parser import Parser
from json import loads
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Tuple
from urllib.parse import parse_qsl
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import fromstring

from werkzeug.datastructures import ImmutableMultiDict


def binary_loads(value: bytes, **parameters: str) -> bytes:
    return value


def plain_loads(value: bytes, **parameters: str) -> str:
    charset = "utf-8"
    if "charset" in parameters:
        charset = parameters["charset"]
    if isinstance(value, bytes):
        try:
            return value.decode(charset)
        # fallback safe decode
        except UnicodeDecodeError:
            return value.decode("ASCII", errors="surrogateescape")
    return value


def json_loads(value: bytes, **parameters: str) -> Any:
    return loads(value)


def xml_loads(value: bytes, **parameters: str) -> Element:
    charset = "utf-8"
    if "charset" in parameters:
        charset = parameters["charset"]
    return fromstring(value.decode(charset))


def urlencoded_form_loads(
    value: bytes, **parameters: str
) -> Mapping[str, Any]:
    # only UTF-8 is conforming
    return ImmutableMultiDict(
        parse_qsl(value.decode("utf-8"), keep_blank_values=True)
    )


def data_form_loads(value: bytes, **parameters: str) -> Mapping[str, Any]:
    charset = "ASCII"
    if "charset" in parameters:
        charset = parameters["charset"]
    decoded = value.decode(charset, errors="surrogateescape")
    boundary = ""
    if "boundary" in parameters:
        boundary = parameters["boundary"]
    parser = Parser()
    mimetype = "multipart/form-data"
    header = f'Content-Type: {mimetype}; boundary="{boundary}"'
    text = "\n\n".join([header, decoded])
    parts = parser.parsestr(text, headersonly=False)
    return ImmutableMultiDict(list(iter_payloads(parts)))


def iter_payloads(parts: Message) -> Iterator[Tuple[str, bytes]]:
    for part in parts.get_payload():
        assert isinstance(part, Message)
        name = part.get_param("name", header="content-disposition")
        assert isinstance(name, str)
        payload = part.get_payload(decode=True)
        assert isinstance(payload, bytes)
        yield name, payload
