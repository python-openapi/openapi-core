import pytest
from jsonschema_path import SchemaPath

from openapi_core.schema.binary import is_base64_schema
from openapi_core.schema.binary import is_binary_schema


def _path(schema_dict):
    return SchemaPath.from_dict(schema_dict)


class TestIsBinarySchema:
    @pytest.mark.parametrize(
        "schema_dict",
        [
            # OAS 3.0 raw octets
            {"type": "string", "format": "binary"},
            # OAS 3.1 content media type (non-text)
            {"type": "string", "contentMediaType": "application/octet-stream"},
            {"type": "string", "contentMediaType": "image/png"},
            # no declared type -> binary keyword is authoritative
            {"format": "binary"},
            # multi-type including string
            {"type": ["string", "null"], "format": "binary"},
        ],
    )
    def test_binary(self, schema_dict):
        assert is_binary_schema(_path(schema_dict)) is True
        # plain-dict form (the shape a jsonschema keyword validator sees)
        assert is_binary_schema(schema_dict) is True

    @pytest.mark.parametrize(
        "schema_dict",
        [
            # base64 text is NOT binary
            {"type": "string", "format": "byte"},
            {"type": "string", "format": "base64"},
            {"type": "string", "contentEncoding": "base64"},
            {"type": "string", "contentEncoding": "base64url"},
            # base64 wins even alongside a non-text contentMediaType
            {
                "type": "string",
                "contentEncoding": "base64",
                "contentMediaType": "application/octet-stream",
            },
            # plain string / other types
            {"type": "string"},
            {"type": "integer"},
            {"type": "object"},
            # text content media type is not opaque binary
            {"type": "string", "contentMediaType": "text/plain"},
            # type explicitly excludes string
            {"type": "integer", "format": "binary"},
        ],
    )
    def test_not_binary(self, schema_dict):
        assert is_binary_schema(_path(schema_dict)) is False
        assert is_binary_schema(schema_dict) is False

    @pytest.mark.parametrize(
        "schema_dict,expected",
        [
            ({"type": "string", "format": "byte"}, True),
            ({"type": "string", "format": "base64"}, True),
            ({"type": "string", "contentEncoding": "base64"}, True),
            ({"type": "string", "format": "binary"}, False),
            ({"type": "string"}, False),
        ],
    )
    def test_is_base64_schema(self, schema_dict, expected):
        assert is_base64_schema(_path(schema_dict)) is expected
