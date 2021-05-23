from itertools import chain
from typing import Dict, Iterator, List, Optional, Union

from werkzeug.datastructures import ImmutableMultiDict, Headers

from openapi_core.spec.paths import SpecPath


def get_aslist(param_or_header: SpecPath) -> bool:
    """Checks if parameter/header is described as list for simpler scenarios"""
    # if schema is not defined it's a complex scenario
    if 'schema' not in param_or_header:
        return False

    schema = param_or_header / 'schema'
    schema_type = schema.getkey('type', 'any')
    # TODO: resolve for 'any' schema type
    return schema_type in ['array', 'object']


def get_style(param_or_header: SpecPath) -> str:
    """Checks parameter/header style for simpler scenarios"""
    if 'style' in param_or_header:
        return str(param_or_header['style'])

    # if "in" not defined then it's a Header
    location = param_or_header.getkey('in', 'header')

    # determine default
    return (
        'simple' if location in ['path', 'header'] else 'form'
    )


def get_explode(param_or_header: SpecPath) -> bool:
    """Checks parameter/header explode for simpler scenarios"""
    explode: bool
    if 'explode' in param_or_header:
        explode = param_or_header['explode']
        return explode

    # determine default
    style = get_style(param_or_header)
    return style == 'form'


def get_value(
    param_or_header: SpecPath,
    location: Union[Dict[str, str], ImmutableMultiDict, Headers],
    name: Optional[str] = None,
) -> Optional[Union[str, List[str]]]:
    """Returns parameter/header value from specific location"""
    name = name or param_or_header['name']

    if name not in location:
        raise KeyError

    # multidict protocol support
    aslist = get_aslist(param_or_header)
    explode = get_explode(param_or_header)
    if aslist and explode:
        assert not isinstance(location, dict)
        value: List[str]
        # very hacky way to support pyramid's webob multidict
        if hasattr(location, 'getall'):
            value = location.getall(name)  # type: ignore
        else:
            value = location.getlist(name)
        return value

    return location[name]


def iter_params(*lists: SpecPath) -> chain:
    iters = map(lambda l: l and iter(l) or [], lists)
    return chain(*iters)
