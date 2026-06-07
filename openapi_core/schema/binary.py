"""Canonical detection of "binary" (opaque, non-text) string schemas.

OpenAPI expresses "this string carries raw, opaque bytes" in two
different ways depending on the version:

* OpenAPI 3.0 uses ``type: string`` together with ``format: binary``
  (raw octets) or ``format: byte`` (base64-encoded *text*).
* OpenAPI 3.1+ aligns with JSON Schema 2020-12, where ``binary``/``byte``
  are no longer defined formats. Raw bytes are described with
  ``contentMediaType`` (e.g. ``application/octet-stream``) and base64
  payloads with ``contentEncoding: base64``. Per JSON Schema Validation
  §8 these content keywords are *annotations, not assertions*, so a
  conforming validator does not reject a value for carrying raw bytes.

This module is the single source of truth for that distinction so the
deserializer, validator, unmarshaller and encoding helpers all agree on
what counts as binary. ``byte``/``base64`` are deliberately *excluded*
from the binary set: those are text (base64) and must keep flowing
through the normal string/text code paths.

Predicates accept either a ``jsonschema_path.SchemaPath`` (used through
most of openapi-core) or a plain ``Mapping`` (the shape jsonschema hands
a custom keyword validator).
"""

from typing import Any
from typing import Mapping
from typing import Optional
from typing import Union

from jsonschema_path import SchemaPath

# ``format`` values denoting base64-encoded *text* (NOT opaque bytes).
# ``base64`` is an accepted alternate spelling for ``byte``.
_BASE64_FORMATS = frozenset({"byte", "base64"})

# JSON Schema 2020-12 ``contentEncoding`` values denoting base64 text.
_BASE64_ENCODINGS = frozenset({"base64", "base64url"})

SchemaLike = Union[SchemaPath, Mapping[str, Any]]


def _read_str(schema: SchemaLike, key: str) -> Optional[str]:
    if isinstance(schema, SchemaPath):
        return (schema / key).read_str(None)
    value = schema.get(key)
    return value if isinstance(value, str) else None


def _read_type(schema: SchemaLike) -> Union[None, str, list[str]]:
    if isinstance(schema, SchemaPath):
        return (schema / "type").read_str_or_list(None)
    value = schema.get("type")
    if value is None or isinstance(value, (str, list)):
        return value
    return None


def type_allows_string(schema: SchemaLike) -> bool:
    """True if a ``string`` instance is permitted at this schema node.

    A missing ``type`` is treated as permissive (OAS 3.1 / JSON Schema
    leaves any value allowed), so the binary/content keywords remain
    authoritative.
    """
    types = _read_type(schema)
    if types is None:
        return True
    if isinstance(types, str):
        return types == "string"
    return "string" in types


def is_base64_schema(schema: SchemaLike) -> bool:
    """True when the schema describes base64-encoded *text*."""
    if _read_str(schema, "format") in _BASE64_FORMATS:
        return True
    return _read_str(schema, "contentEncoding") in _BASE64_ENCODINGS


def is_binary_schema(schema: SchemaLike) -> bool:
    """True when the schema describes an opaque, non-text byte payload.

    Covers OAS 3.0 ``format: binary`` and OAS 3.1
    ``contentMediaType`` of a non-``text/*`` media type. Base64 text
    (``format: byte``/``base64`` or ``contentEncoding``) is explicitly
    excluded -- it stays on the normal text path.
    """
    if not isinstance(schema, (SchemaPath, Mapping)):
        return False
    if not type_allows_string(schema):
        return False
    if is_base64_schema(schema):
        return False
    if _read_str(schema, "format") == "binary":
        return True
    content_media_type = _read_str(schema, "contentMediaType")
    if content_media_type is not None and not content_media_type.startswith(
        "text/"
    ):
        return True
    return False
