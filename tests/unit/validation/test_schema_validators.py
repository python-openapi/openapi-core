import pytest
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue


class TestSchemaValidate:
    @pytest.fixture
    def spec(self):
        spec_dict = {}
        return SchemaPath.from_dict(spec_dict)

    @pytest.fixture
    def validator_factory(self, spec):
        def create_validator(schema):
            return oas30_write_schema_validators_factory.create(spec, schema)

        return create_validator

    def test_string_format_custom_missing(self, validator_factory):
        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = SchemaPath.from_dict(schema)
        value = "x"

        validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_integer_minimum_invalid(self, value, validator_factory):
        schema = {
            "type": "integer",
            "minimum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_integer_minimum(self, value, validator_factory):
        schema = {
            "type": "integer",
            "minimum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_integer_maximum_invalid(self, value, validator_factory):
        schema = {
            "type": "integer",
            "maximum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_integer_maximum(self, value, validator_factory):
        schema = {
            "type": "integer",
            "maximum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 2, 4])
    def test_integer_multiple_of_invalid(self, value, validator_factory):
        schema = {
            "type": "integer",
            "multipleOf": 3,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [3, 6, 18])
    def test_integer_multiple_of(self, value, validator_factory):
        schema = {
            "type": "integer",
            "multipleOf": 3,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_number_minimum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [3, 4, 5])
    def test_number_minimum(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_number_exclusive_minimum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
            "exclusiveMinimum": True,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_number_exclusive_minimum(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
            "exclusiveMinimum": True,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_number_maximum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_number_maximum(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [3, 4, 5])
    def test_number_exclusive_maximum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
            "exclusiveMaximum": True,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_number_exclusive_maximum(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
            "exclusiveMaximum": True,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 2, 4])
    def test_number_multiple_of_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "multipleOf": 3,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [3, 6, 18])
    def test_number_multiple_of(self, value, validator_factory):
        schema = {
            "type": "number",
            "multipleOf": 3,
        }
        spec = SchemaPath.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    def test_additional_properties_omitted_default_allows_extra(self, spec):
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        schema = SchemaPath.from_dict(schema_dict)
        value = {
            "name": "openapi-core",
            "extra": "allowed by default",
        }

        result = oas30_write_schema_validators_factory.create(
            spec, schema
        ).validate(value)

        assert result is None

    def test_additional_properties_omitted_strict_rejects_extra(self, spec):
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        schema = SchemaPath.from_dict(schema_dict)
        value = {
            "name": "openapi-core",
            "extra": "not allowed in strict mode",
        }

        with pytest.raises(InvalidSchemaValue):
            oas30_write_schema_validators_factory.create(
                spec,
                schema,
                forbid_unspecified_additional_properties=True,
            ).validate(value)

    def test_additional_properties_true_strict_allows_extra(self, spec):
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": True,
        }
        schema = SchemaPath.from_dict(schema_dict)
        value = {
            "name": "openapi-core",
            "extra": "explicitly allowed",
        }

        result = oas30_write_schema_validators_factory.create(
            spec,
            schema,
            forbid_unspecified_additional_properties=True,
        ).validate(value)

        assert result is None

    def test_enforce_properties_required_rejects_missing_property(self, spec):
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }
        schema = SchemaPath.from_dict(schema_dict)

        with pytest.raises(InvalidSchemaValue):
            oas30_write_schema_validators_factory.create(
                spec,
                schema,
                enforce_properties_required=True,
            ).validate({"name": "openapi-core"})

    def test_enforce_properties_required_ignores_write_only_fields(self, spec):
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "secret": {
                    "type": "string",
                    "writeOnly": True,
                },
            },
            "required": ["name"],
        }
        schema = SchemaPath.from_dict(schema_dict)

        result = oas30_write_schema_validators_factory.create(
            spec,
            schema,
            enforce_properties_required=True,
        ).validate({"name": "openapi-core"})

        assert result is None

    def test_enforce_properties_required_applies_to_nested_composed_schemas(
        self,
        spec,
    ):
        schema_dict = {
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                    },
                },
                {
                    "type": "object",
                    "properties": {
                        "meta": {
                            "type": "object",
                            "properties": {
                                "version": {"type": "integer"},
                            },
                        }
                    },
                },
            ]
        }
        schema = SchemaPath.from_dict(schema_dict)

        with pytest.raises(InvalidSchemaValue):
            oas30_write_schema_validators_factory.create(
                spec,
                schema,
                enforce_properties_required=True,
            ).validate({"name": "openapi-core", "meta": {}})



class TestSchemaValidatorCacheIsolation:
    """The per-resolver cache must keep ``_schema_needs_state`` answers
    independent across distinct OpenAPI specs that happen to share
    JSON-pointer paths.

    Regression test for the ``SchemaPath``-keyed cache: ``SchemaPath``
    equality is path-only (inherited from ``pathable.BasePath``), so a
    ``dict``-keyed cache would collide on identical paths regardless of
    what the paths actually resolve to. The bug is silent in production
    because all evolved schemas come from one spec, but bites in any
    process that loads more than one.
    """

    def test_disjoint_specs_with_colliding_paths(self):
        # Both specs have a value at ``anyOf/0`` but one is a leaf
        # string and the other carries oneOf -- only the second should
        # report needs_state=True.
        from openapi_core.validation.schemas.validators import SchemaValidator

        spec_simple = SchemaPath.from_dict(
            {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        )
        spec_composed = SchemaPath.from_dict(
            {
                "anyOf": [
                    {
                        "type": "object",
                        "properties": {
                            "x": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "integer"},
                                ]
                            }
                        },
                    },
                    {"type": "integer"},
                ]
            }
        )

        # Each branch's value at anyOf/0 has the SAME SchemaPath
        # (anyOf#0) but disjoint contents.
        simple_branch = spec_simple / "anyOf" / 0
        composed_branch = spec_composed / "anyOf" / 0
        assert simple_branch == composed_branch  # path-only equality
        assert hash(simple_branch) == hash(composed_branch)

        # The cache must distinguish them by spec.
        assert SchemaValidator._schema_needs_state(simple_branch) is False
        assert SchemaValidator._schema_needs_state(composed_branch) is True
        # And the order doesn't matter -- ask in reverse.
        spec_simple_2 = SchemaPath.from_dict(
            {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        )
        spec_composed_2 = SchemaPath.from_dict(
            {
                "anyOf": [
                    {"oneOf": [{"type": "string"}]},
                    {"type": "integer"},
                ]
            }
        )
        assert (
            SchemaValidator._schema_needs_state(
                spec_composed_2 / "anyOf" / 0
            )
            is True
        )
        assert (
            SchemaValidator._schema_needs_state(
                spec_simple_2 / "anyOf" / 0
            )
            is False
        )

    def test_cache_evicts_on_resolver_collection(self):
        # When a spec's resolver is garbage-collected, its cache slot
        # is dropped. This both prevents the cache from pinning the
        # spec in memory and forecloses on the classic id()-reuse
        # hazard (a freshly allocated resolver cannot inherit stale
        # answers from a collected one at the same address).
        import gc

        from openapi_core.validation.schemas._caches import _caches
        from openapi_core.validation.schemas.validators import SchemaValidator

        before = len(_caches)
        spec = SchemaPath.from_dict(
            {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        )
        SchemaValidator._schema_needs_state(spec)
        # Capturing one extra slot is what we expect.
        assert len(_caches) == before + 1

        # Drop the only outside reference; the cache slot must follow.
        del spec
        gc.collect()
        assert len(_caches) == before
