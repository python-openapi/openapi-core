from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.schema.protocols import SuportsGetAll
from openapi_core.schema.protocols import SuportsGetList


def get_style(param_or_header: SchemaPath) -> str:
    """Checks parameter/header style for simpler scenarios"""
    if "style" in param_or_header:
        assert isinstance(param_or_header["style"], str)
        return param_or_header["style"]

    # if "in" not defined then it's a Header
    location = param_or_header.getkey("in", "header")

    # determine default
    return "simple" if location in ["path", "header"] else "form"


def get_explode(param_or_header: SchemaPath) -> bool:
    """Checks parameter/header explode for simpler scenarios"""
    if "explode" in param_or_header:
        assert isinstance(param_or_header["explode"], bool)
        return param_or_header["explode"]

    # determine default
    style = get_style(param_or_header)
    return style == "form"
