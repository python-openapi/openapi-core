import pytest
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.validators import _HAS_CANONICAL
from openapi_core.validation.schemas.validators import SchemaValidator


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


class TestSchemaValidateState:
    SCHEMA_DICT = {
        "type": "object",
        "properties": {
            "x": {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        },
    }
    VALUE = {"x": "hi"}

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        # Keep this class's cache observations isolated from other tests.
        SchemaValidator._needs_state_cache.clear()
        yield
        SchemaValidator._needs_state_cache.clear()

    @pytest.fixture
    def cache(self):
        return SchemaValidator._needs_state_cache

    @pytest.fixture
    def validator_and_prop_factory(self):
        # Build a validator over a freshly loaded spec and return it
        # alongside the SchemaPath the cache keys on for property "x".
        root = SchemaPath.from_dict({})

        def _build(schema_dict):
            spec = SchemaPath.from_dict(schema_dict)
            validator = oas30_write_schema_validators_factory.create(
                root, spec
            )
            prop = spec / "properties" / "x"
            return validator, prop

        return _build

    def test_cold_pass_populates_cache(
        self, cache, validator_and_prop_factory
    ):
        validator, prop = validator_and_prop_factory(self.SCHEMA_DICT)
        assert prop not in cache

        validator.validate_state(self.VALUE)

        # oneOf under "x" -> a ValidationState is worthwhile.
        assert cache[prop] is True

    def test_warm_pass_reads_cached_answer(
        self, cache, validator_and_prop_factory
    ):
        validator, prop = validator_and_prop_factory(self.SCHEMA_DICT)
        validator.validate_state(self.VALUE)  # prime
        # Poison the entry: a genuine cache hit returns this value
        # unchanged, whereas a recompute would overwrite it back to True.
        cache[prop] = False

        validator.validate_state(self.VALUE)

        assert cache[prop] is False

    def test_distinct_spec_does_not_collide(
        self, cache, validator_and_prop_factory
    ):
        # Two separately loaded specs with identical contents have
        # distinct identity, so their equally-pathed property schemas
        # occupy separate cache slots instead of colliding.
        validator_a, prop_a = validator_and_prop_factory(self.SCHEMA_DICT)
        validator_b, prop_b = validator_and_prop_factory(self.SCHEMA_DICT)

        validator_a.validate_state(self.VALUE)
        assert prop_a in cache
        assert prop_b not in cache

        validator_b.validate_state(self.VALUE)
        assert cache[prop_a] is True
        assert cache[prop_b] is True


class TestSchemaValidateStateRefDedup:
    # A single composed schema reached through two different $ref aliases.
    SCHEMA_DICT = {
        "type": "object",
        "properties": {
            "a": {"$ref": "#/$defs/Composed"},
            "b": {"$ref": "#/$defs/Composed"},
        },
        "$defs": {
            "Composed": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
        },
    }
    VALUE = {"a": "hi", "b": 1}

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        SchemaValidator._needs_state_cache.clear()
        yield
        SchemaValidator._needs_state_cache.clear()

    @pytest.fixture
    def cache(self):
        return SchemaValidator._needs_state_cache

    @pytest.fixture
    def validator_and_props_factory(self):
        root = SchemaPath.from_dict({})

        def _build(schema_dict):
            spec = SchemaPath.from_dict(schema_dict)
            validator = oas30_write_schema_validators_factory.create(
                root, spec
            )
            prop_a = spec / "properties" / "a"
            prop_b = spec / "properties" / "b"
            canonical = spec / "$defs" / "Composed"
            return validator, prop_a, prop_b, canonical

        return _build

    @pytest.mark.xfail(
        condition=not _HAS_CANONICAL,
        strict=True,
        reason=(
            "Without SchemaPath.canonical the cache keys on the navigation "
            "path, so each $ref alias gets its own slot. With canonical "
            "keying the aliases collapse to a single entry."
        ),
    )
    def test_aliases_to_same_node_share_one_cache_slot(
        self, cache, validator_and_props_factory
    ):
        validator, prop_a, prop_b, canonical = validator_and_props_factory(
            self.SCHEMA_DICT
        )

        validator.validate_state(self.VALUE)

        assert len(cache) == 1
        assert prop_a not in cache
        assert prop_b not in cache
        assert cache[canonical] is True
