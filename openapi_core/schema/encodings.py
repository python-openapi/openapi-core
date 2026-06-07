from typing import Optional
from typing import cast

from jsonschema_path import SchemaPath

from openapi_core.schema.binary import is_binary_schema


def get_content_type(
    prop_schema: SchemaPath, encoding: Optional[SchemaPath]
) -> str:
    if encoding is None:
        return get_default_content_type(prop_schema, encoding=False)

    if "contentType" not in encoding:
        return get_default_content_type(prop_schema, encoding=True)

    return cast(str, encoding["contentType"])


def get_default_content_type(
    prop_schema: Optional[SchemaPath], encoding: bool = False
) -> str:
    if prop_schema is None:
        return "text/plain"

    prop_type = (prop_schema / "type").read_str(None)
    if prop_type is None:
        return "text/plain" if encoding else "application/octet-stream"

    if prop_type == "string" and is_binary_schema(prop_schema):
        # Opaque binary (OAS 3.0 ``format: binary`` or OAS 3.1
        # ``contentMediaType``) defaults to octet-stream. base64 text
        # (``byte``/``base64``/``contentEncoding``) is NOT binary and
        # falls through to ``text/plain`` below.
        return "application/octet-stream"

    if prop_type == "object":
        return "application/json"

    if prop_type == "array":
        prop_items = prop_schema / "items"
        return get_default_content_type(prop_items, encoding=encoding)

    return "text/plain"
