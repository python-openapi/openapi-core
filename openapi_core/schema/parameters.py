from typing import Tuple

from jsonschema_path import SchemaPath


def get_style(
    param_or_header: SchemaPath, default_location: str = "header"
) -> str:
    """Checks parameter/header style for simpler scenarios"""
    if "style" in param_or_header:
        assert isinstance(param_or_header["style"], str)
        return param_or_header["style"]

    location = param_or_header.getkey("in", default_location)

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


def get_style_and_explode(
    param_or_header: SchemaPath, default_location: str = "header"
) -> Tuple[str, bool]:
    """Checks parameter/header explode for simpler scenarios"""
    style = get_style(param_or_header, default_location=default_location)
    if "explode" in param_or_header:
        assert isinstance(param_or_header["explode"], bool)
        return style, param_or_header["explode"]

    return style, style == "form"
