from itertools import chain


def get_aslist(param_or_header):
    """Checks if parameter/header is described as list for simpler scenarios"""
    # if schema is not defined it's a complex scenario
    if "schema" not in param_or_header:
        return False

    schema = param_or_header / "schema"
    schema_type = schema.getkey("type", "any")
    # TODO: resolve for 'any' schema type
    return schema_type in ["array", "object"]


def get_style(param_or_header):
    """Checks parameter/header style for simpler scenarios"""
    if "style" in param_or_header:
        return param_or_header["style"]

    # if "in" not defined then it's a Header
    location = param_or_header.getkey("in", "header")

    # determine default
    return "simple" if location in ["path", "header"] else "form"


def get_explode(param_or_header):
    """Checks parameter/header explode for simpler scenarios"""
    if "explode" in param_or_header:
        return param_or_header["explode"]

    # determine default
    style = get_style(param_or_header)
    return style == "form"


def get_value(param_or_header, location, name=None):
    """Returns parameter/header value from specific location"""
    name = name or param_or_header["name"]

    if name not in location:
        raise KeyError

    aslist = get_aslist(param_or_header)
    explode = get_explode(param_or_header)
    if aslist and explode:
        if hasattr(location, "getall"):
            return location.getall(name)
        return location.getlist(name)

    return location[name]


def iter_params(*lists):
    iters = map(lambda l: l and iter(l) or [], lists)
    return chain(*iters)
