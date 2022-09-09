from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from werkzeug.datastructures import Headers

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


def get_value(
    param_or_header: Spec,
    location: Union[Headers, Dict[str, Any]],
    name: Optional[str] = None,
) -> Any:
    """Returns parameter/header value from specific location"""
    name = name or param_or_header["name"]

    if name not in location:
        raise KeyError

    aslist = get_aslist(param_or_header)
    explode = get_explode(param_or_header)
    if aslist and explode:
        if isinstance(location, SuportsGetAll):
            return location.getall(name)
        if isinstance(location, SuportsGetList):
            return location.getlist(name)

    return location[name]
