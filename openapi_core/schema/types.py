"""Helpers for OpenAPI ``type`` (string or list of strings).

OAS 3.1 and 3.2 allow the ``type`` keyword to be either a single string or
a list of strings (e.g. ``type: ["integer", "null"]``). OAS 3.0 only allows
a single string. Several places in the code need to make decisions based on
the *structural* type implied by the schema (array vs. object vs. primitive)
without caring which side of the version split they are on; this module
centralises that mapping.
"""

from typing import Iterable
from typing import Optional
from typing import Union


def pick_style_type(
    schema_type: Optional[Union[str, Iterable[str]]],
) -> str:
    """Pick the structural type used by style/multipart deserializers.

    Style loaders need to know whether the wire form should be parsed as an
    array, an object, or a single scalar. They do not need to know which
    primitive type the leaf will eventually become — that is the schema
    caster's job.

    For multi-type schemas the priority is ``array`` > ``object`` >
    primitive. Primitive (or unknown) is represented by an empty string to
    match the historical default returned by ``read_str_or_list("")``.
    """
    if schema_type is None:
        return ""
    if isinstance(schema_type, str):
        return schema_type
    types = list(schema_type)
    if "array" in types:
        return "array"
    if "object" in types:
        return "object"
    return ""
