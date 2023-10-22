import pytest
from jsonschema_path import SchemaPath

from openapi_core.casting.schemas import oas31_schema_casters_factory
from openapi_core.casting.schemas.exceptions import CastError


class TestSchemaCaster:
    @pytest.fixture
    def caster_factory(self):
        def create_caster(schema):
            return oas31_schema_casters_factory.create(schema)

        return create_caster

    @pytest.mark.parametrize(
        "schema_type,value,expected",
        [
            ("integer", "2", 2),
            ("number", "3.14", 3.14),
            ("boolean", "false", False),
            ("boolean", "true", True),
        ],
    )
    def test_primitive_flat(
        self, caster_factory, schema_type, value, expected
    ):
        spec = {
            "type": schema_type,
        }
        schema = SchemaPath.from_dict(spec)

        result = caster_factory(schema).cast(value)

        assert result == expected

    def test_array_invalid_type(self, caster_factory):
        spec = {
            "type": "array",
            "items": {
                "type": "number",
            },
        }
        schema = SchemaPath.from_dict(spec)
        value = ["test", "test2"]

        with pytest.raises(CastError):
            caster_factory(schema).cast(value)

    @pytest.mark.parametrize("value", [3.14, "foo", b"foo"])
    def test_array_invalid_value(self, value, caster_factory):
        spec = {
            "type": "array",
            "items": {
                "oneOf": [{"type": "number"}, {"type": "string"}],
            },
        }
        schema = SchemaPath.from_dict(spec)

        with pytest.raises(
            CastError, match=f"Failed to cast value to array type: {value}"
        ):
            caster_factory(schema).cast(value)
