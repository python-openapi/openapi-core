from email.parser import Parser
from typing import Any
from typing import Dict
from typing import Union
from urllib.parse import parse_qsl


def plain_loads(value: Union[str, bytes]) -> str:
    if isinstance(value, bytes):
        value = value.decode("ASCII", errors="surrogateescape")
    return value


def urlencoded_form_loads(value: Any) -> Dict[str, Any]:
    return dict(parse_qsl(value))


def data_form_loads(value: Union[str, bytes]) -> Dict[str, Any]:
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
