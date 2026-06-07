import pytest
from jsonschema_path import SchemaPath
from openapi_schema_validator import OAS31_BASE_DIALECT_ID
from openapi_schema_validator import OAS32_BASE_DIALECT_ID

from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas import oas31_schema_validators_factory
from openapi_core.validation.schemas import oas32_schema_validators_factory
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
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
        strict=True,
        reason=(
            "The cache keys on the navigation path, so each $ref "
            "alias gets its own slot. Once the cache keys on canonical "
            "the aliases collapse to a single entry."
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


class TestBinaryAwareValidate:
    """A ``bytes`` payload validates against a binary string schema,
    while plain (non-binary) string schemas still reject ``bytes``.
    """

    @pytest.fixture
    def spec(self):
        return SchemaPath.from_dict({})

    @pytest.fixture(
        params=[
            oas30_write_schema_validators_factory,
            oas31_schema_validators_factory,
            oas32_schema_validators_factory,
        ],
        ids=["oas30", "oas31", "oas32"],
    )
    def factory(self, request):
        return request.param

    def _validate(self, factory, spec, schema_dict, value):
        schema = SchemaPath.from_dict(schema_dict)
        factory.create(spec, schema).validate(value)

    def test_bytes_valid_against_binary_format(self, factory, spec):
        self._validate(
            factory, spec, {"type": "string", "format": "binary"}, b"\xff\xfe"
        )

    def test_bytes_valid_against_content_media_type(self, factory, spec):
        self._validate(
            factory,
            spec,
            {"type": "string", "contentMediaType": "application/octet-stream"},
            b"\xff\xfe",
        )

    def test_bytes_rejected_against_plain_string(self, factory, spec):
        with pytest.raises(InvalidSchemaValue):
            self._validate(factory, spec, {"type": "string"}, b"\xff\xfe")

    def test_bytes_rejected_against_byte_base64_format(self, factory, spec):
        # ``byte`` is base64 *text*, not opaque binary: arbitrary bytes
        # must not slip through as a string.
        with pytest.raises(InvalidSchemaValue):
            self._validate(
                factory,
                spec,
                {"type": "string", "format": "byte"},
                b"\xff\xfe",
            )

    def test_bytes_valid_in_oneof_binary_branch(self, factory, spec):
        schema_dict = {
            "oneOf": [
                {"type": "string", "format": "binary"},
                {"type": "object"},
            ]
        }
        self._validate(factory, spec, schema_dict, b"\xff\xfe")

    def test_bytes_valid_in_anyof_binary_branch(self, factory, spec):
        schema_dict = {
            "anyOf": [
                {"type": "string", "format": "binary"},
                {"type": "integer"},
            ]
        }
        self._validate(factory, spec, schema_dict, b"\xff\xfe")

    def test_bytes_valid_in_nested_object_property(self, factory, spec):
        schema_dict = {
            "type": "object",
            "properties": {
                "file": {"type": "string", "format": "binary"},
            },
            "required": ["file"],
        }
        self._validate(factory, spec, schema_dict, {"file": b"\xff\xfe"})

    def test_string_assertion_keywords_do_not_crash_on_bytes(
        self, factory, spec
    ):
        # ``pattern`` raises TypeError on bytes in plain jsonschema; the
        # binary node treats the payload as opaque and skips it.
        schema_dict = {
            "type": "string",
            "format": "binary",
            "pattern": "^a",
            "minLength": 100,
            "maxLength": 1,
        }
        self._validate(factory, spec, schema_dict, b"\xff\xfe")

    def test_plain_string_still_validates_normally(self, factory, spec):
        self._validate(factory, spec, {"type": "string"}, "hello")

    def test_input_value_not_mutated(self, factory, spec):
        schema_dict = {
            "type": "object",
            "properties": {
                "file": {"type": "string", "format": "binary"},
            },
        }
        value = {"file": b"\xff\xfe"}
        self._validate(factory, spec, schema_dict, value)
        assert value == {"file": b"\xff\xfe"}
        assert isinstance(value["file"], bytes)

    @pytest.mark.parametrize(
        "dialect_factory, dialect_id",
        [
            (oas31_schema_validators_factory, OAS31_BASE_DIALECT_ID),
            (oas32_schema_validators_factory, OAS32_BASE_DIALECT_ID),
        ],
        ids=["oas31", "oas32"],
    )
    def test_bytes_valid_with_explicit_dialect_in_schema(
        self, spec, dialect_factory, dialect_id
    ):
        # The fixture-driven tests rely on the *default* dialect; here
        # the schema declares its own dialect via ``$schema`` so the
        # ``_get_dialect_id`` read-from-schema branch is covered too.
        schema_dict = {
            "$schema": dialect_id,
            "type": "string",
            "format": "binary",
        }
        self._validate(dialect_factory, spec, schema_dict, b"\xff\xfe")

    def test_bytes_on_non_oas_dialect_keeps_binary_handling(self, spec):
        # Boundary characterization: a schema opting into a *stock* JSON
        # Schema dialect (not an OAS dialect) still accepts opaque bytes
        # today, because binary handling wraps whatever validator class
        # the dialect resolves to. If binary handling is ever delegated
        # to the per-dialect validator classes, this path needs its own
        # coverage -- so pin the current behaviour explicitly.
        schema_dict = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "string",
            "format": "binary",
        }
        self._validate(
            oas31_schema_validators_factory, spec, schema_dict, b"\xff\xfe"
        )
