import pytest
from jsonschema_path import SchemaPath

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.casting.schemas.factories import SchemaCastersFactory


class TestSchemaCaster:
    @pytest.fixture
    def caster_factory(self):
        def create_caster(schema):
            return SchemaCastersFactory().create(schema)

        return create_caster

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
            caster_factory(schema)(value)

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
            caster_factory(schema)(value)
