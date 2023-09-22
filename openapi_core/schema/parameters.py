import re
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional

from openapi_core.schema.protocols import SuportsGetAll
from openapi_core.schema.protocols import SuportsGetList
from openapi_core.spec import Spec


def get_aslist(param_or_header: Spec) -> bool:
    """Checks if parameter/header is described as list for simpler scenarios"""
    # if schema is not defined it's a complex scenario
    if "schema" not in param_or_header:
        return False

    schema = param_or_header / "schema"
    schema_type = schema.getkey("type", "any")
    # TODO: resolve for 'any' schema type
    return schema_type in ["array", "object"]


def get_style(param_or_header: Spec) -> str:
    """Checks parameter/header style for simpler scenarios"""
    if "style" in param_or_header:
        assert isinstance(param_or_header["style"], str)
        return param_or_header["style"]

    # if "in" not defined then it's a Header
    location = param_or_header.getkey("in", "header")

    # determine default
    return "simple" if location in ["path", "header"] else "form"


def get_explode(param_or_header: Spec) -> bool:
    """Checks parameter/header explode for simpler scenarios"""
    if "explode" in param_or_header:
        assert isinstance(param_or_header["explode"], bool)
        return param_or_header["explode"]

    # determine default
    style = get_style(param_or_header)
    return style == "form"


def get_deep_object_value(
    location: Mapping[str, Any],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    values = {}
    for key, value in location.items():
        # Split the key from the brackets.
        key_split = re.split(pattern=r"\[|\]", string=key)
        if key_split[0] == name:
            values[key_split[1]] = value
    return values
