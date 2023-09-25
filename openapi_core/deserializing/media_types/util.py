from email.parser import Parser
from typing import Any
from typing import Dict
from typing import Union
from urllib.parse import parse_qsl


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


def urlencoded_form_loads(value: Any, **parameters: str) -> Dict[str, Any]:
    return dict(parse_qsl(value))


def data_form_loads(
    value: Union[str, bytes], **parameters: str
) -> Dict[str, Any]:
    if isinstance(value, bytes):
        value = value.decode("ASCII", errors="surrogateescape")
    parser = Parser()
    parts = parser.parsestr(value, headersonly=False)
    return {
        part.get_param("name", header="content-disposition"): part.get_payload(
            decode=True
        )
        for part in parts.get_payload()
    }
