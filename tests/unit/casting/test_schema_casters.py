import pytest
from jsonschema_path import SchemaPath

from openapi_core.casting.schemas import oas31_schema_casters_factory
from openapi_core.casting.schemas.exceptions import CastError


class TestSchemaCaster:
    @pytest.fixture
    def spec(self):
        spec_dict = {}
        return SchemaPath.from_dict(spec_dict)

    @pytest.fixture
    def caster_factory(self, spec):
        def create_caster(schema):
            return oas31_schema_casters_factory.create(spec, schema)

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

    @pytest.mark.parametrize(
        "composite_type,schema_type,value,expected",
        [
            ("allOf", "integer", "2", 2),
            ("anyOf", "number", "3.14", 3.14),
            ("oneOf", "boolean", "false", False),
            ("oneOf", "boolean", "true", True),
        ],
    )
    def test_composite_primitive(
        self, caster_factory, composite_type, schema_type, value, expected
    ):
        spec = {
            composite_type: [{"type": schema_type}],
        }
        schema = SchemaPath.from_dict(spec)

        result = caster_factory(schema).cast(value)

        assert result == expected

    @pytest.mark.parametrize(
        "schemas,value,expected",
        [
            # If string is evaluated first, it succeeds and returns string
            ([{"type": "string"}, {"type": "integer"}], "123", "123"),
            # If integer is evaluated first, it succeeds and returns int
            ([{"type": "integer"}, {"type": "string"}], "123", 123),
        ],
    )
    def test_oneof_greedy_casting_edge_case(
        self, caster_factory, schemas, value, expected
    ):
        """
        Documents the edge case that AnyCaster's oneOf/anyOf logic is greedy.
        It returns the first successfully casted value based on the order in the list.
        """
        spec = {
            "oneOf": schemas,
        }
        schema = SchemaPath.from_dict(spec)

        result = caster_factory(schema).cast(value)

        assert result == expected
        # Ensure exact type matches to prevent 123 == "123" test bypass issues
        assert type(result) is type(expected)

    def test_allof_sequential_mutation_edge_case(self, caster_factory):
        """
        Documents the edge case that AnyCaster's allOf logic sequentially mutates the value.
        The first schema casts "2" to an int (2). The second schema (number)
        receives the int 2, casts it to float (2.0), and returns the float.
        """
        spec = {
            "allOf": [{"type": "integer"}, {"type": "number"}],
        }
        schema = SchemaPath.from_dict(spec)
        value = "2"

        result = caster_factory(schema).cast(value)

        # "2" -> int(2) -> float(2.0)
        assert result == 2.0
        assert type(result) is float
