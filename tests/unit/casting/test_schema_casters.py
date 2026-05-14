import pytest
from jsonschema_path import SchemaPath

from openapi_core.casting.schemas import oas30_write_schema_casters_factory
from openapi_core.casting.schemas import oas31_schema_casters_factory
from openapi_core.casting.schemas import oas32_schema_casters_factory
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
        "schema_types,value,expected",
        [
            # First candidate wins when it succeeds.
            (["string", "number", "boolean"], "12567", "12567"),
            (["integer", "string"], "42", 42),
            (["number", "string"], "3.14", 3.14),
            (["boolean", "string"], "true", True),
            # Second candidate wins when the first one cannot coerce.
            (["integer", "string"], "abc", "abc"),
            (["boolean", "string"], "maybe", "maybe"),
            # ``null`` entries are skipped — they are short-circuited
            # upstream by ``SchemaCaster.cast`` before MultiTypeCaster runs.
            (["integer", "null"], "42", 42),
            (["null", "integer"], "42", 42),
        ],
    )
    def test_oas31_multi_type(
        self, caster_factory, schema_types, value, expected
    ):
        """OAS 3.1 list-style ``type`` coerces to the first matching candidate."""
        spec = {
            "type": schema_types,
        }
        schema = SchemaPath.from_dict(spec)

        result = caster_factory(schema).cast(value)

        assert result == expected
        assert type(result) is type(expected)

    def test_oas31_multi_type_no_candidate_raises(self, caster_factory):
        """When no candidate succeeds, raise once with the full type list."""
        spec = {"type": ["integer", "boolean"]}
        schema = SchemaPath.from_dict(spec)

        with pytest.raises(CastError) as excinfo:
            caster_factory(schema).cast("not-a-number")

        # ``CastError.type`` carries the full declared list, not just the
        # last attempted candidate.
        assert excinfo.value.type == ["integer", "boolean"]

    def test_oas31_multi_type_null_value(self, caster_factory):
        """``None`` is short-circuited by SchemaCaster.cast, regardless of
        whether MultiTypeCaster is dispatched."""
        spec = {"type": ["integer", "null"]}
        schema = SchemaPath.from_dict(spec)

        assert caster_factory(schema).cast(None) is None

    def test_oas31_multi_type_nested_object(self, caster_factory):
        """A property declared multi-type is recursively coerced inside an
        object."""
        spec = {
            "type": "object",
            "properties": {
                "count": {"type": ["integer", "null"]},
                "name": {"type": ["string", "null"]},
            },
        }
        schema = SchemaPath.from_dict(spec)

        result = caster_factory(schema).cast({"count": "5", "name": "foo"})

        assert result == {"count": 5, "name": "foo"}
        assert type(result["count"]) is int

    def test_oas31_multi_type_nested_array_items(self, caster_factory):
        """Array items declared multi-type are coerced per element."""
        spec = {
            "type": "array",
            "items": {"type": ["integer", "string"]},
        }
        schema = SchemaPath.from_dict(spec)

        result = caster_factory(schema).cast(["1", "2", "abc"])

        assert result == [1, 2, "abc"]

    def test_oas31_multi_type_object_or_null(self, caster_factory):
        """An ``object``-or-null schema still walks properties when the value
        is an object."""
        spec = {
            "type": ["object", "null"],
            "properties": {"count": {"type": "integer"}},
        }
        schema = SchemaPath.from_dict(spec)

        result = caster_factory(schema).cast({"count": "7"})

        assert result == {"count": 7}

    def test_oas32_multi_type(self):
        """OAS 3.2 inherits the OAS 3.1 multi-type behavior."""
        spec_dict = {}
        spec = SchemaPath.from_dict(spec_dict)
        schema = SchemaPath.from_dict({"type": ["integer", "string"]})

        result = oas32_schema_casters_factory.create(spec, schema).cast("42")

        assert result == 42

    def test_oas30_rejects_multi_type(self):
        """OAS 3.0 has no notion of multi-type — dispatch must raise."""
        spec_dict = {}
        spec = SchemaPath.from_dict(spec_dict)
        schema = SchemaPath.from_dict({"type": ["string", "null"]})

        with pytest.raises(TypeError, match="multiple types"):
            oas30_write_schema_casters_factory.create(spec, schema).cast(
                "anything"
            )

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
