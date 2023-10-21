from email.parser import Parser
from json import loads
from typing import Any
from typing import Mapping
from typing import Union
from urllib.parse import parse_qsl
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import fromstring

from werkzeug.datastructures import ImmutableMultiDict


def binary_loads(value: Union[str, bytes], **parameters: str) -> bytes:
    charset = "utf-8"
    if "charset" in parameters:
        charset = parameters["charset"]
    if isinstance(value, str):
        return value.encode(charset)
    return value


def plain_loads(value: Union[str, bytes], **parameters: str) -> str:
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


def json_loads(value: Union[str, bytes], **parameters: str) -> Any:
    return loads(value)


def xml_loads(value: Union[str, bytes], **parameters: str) -> Element:
    return fromstring(value)


def urlencoded_form_loads(value: Any, **parameters: str) -> Mapping[str, Any]:
    return ImmutableMultiDict(parse_qsl(value))


def data_form_loads(
    value: Union[str, bytes], **parameters: str
) -> Mapping[str, Any]:
    if isinstance(value, bytes):
        value = value.decode("ASCII", errors="surrogateescape")
    boundary = ""
    if "boundary" in parameters:
        boundary = parameters["boundary"]
    parser = Parser()
    mimetype = "multipart/form-data"
    header = f'Content-Type: {mimetype}; boundary="{boundary}"'
    text = "\n\n".join([header, value])
    parts = parser.parsestr(text, headersonly=False)
    return ImmutableMultiDict(
        [
            (
                part.get_param("name", header="content-disposition"),
                part.get_payload(decode=True),
            )
            for part in parts.get_payload()
        ]
    )
