from typing import Optional
from typing import cast

from jsonschema_path import SchemaPath


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

    prop_type = prop_schema.getkey("type")
    if prop_type is None:
        return "text/plain" if encoding else "application/octet-stream"

    prop_format = prop_schema.getkey("format")
    if prop_type == "string" and prop_format in ["binary", "base64"]:
        return "application/octet-stream"

    if prop_type == "object":
        return "application/json"

    if prop_type == "array":
        prop_items = prop_schema / "items"
        return get_default_content_type(prop_items, encoding=encoding)

    return "text/plain"
