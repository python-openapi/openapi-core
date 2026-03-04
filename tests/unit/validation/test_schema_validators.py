import pytest
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue


class TestSchemaValidate:
    @pytest.fixture
    def validator_factory(self):
        def create_validator(schema):
            return oas30_write_schema_validators_factory.create(schema)

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

    def test_additional_properties_omitted_default_allows_extra(self):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        spec = SchemaPath.from_dict(schema)
        value = {
            "name": "openapi-core",
            "extra": "allowed by default",
        }

        result = oas30_write_schema_validators_factory.create(spec).validate(
            value
        )

        assert result is None

    def test_additional_properties_omitted_strict_rejects_extra(self):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        spec = SchemaPath.from_dict(schema)
        value = {
            "name": "openapi-core",
            "extra": "not allowed in strict mode",
        }

        with pytest.raises(InvalidSchemaValue):
            oas30_write_schema_validators_factory.create(
                spec,
                strict_additional_properties=True,
            ).validate(value)

    def test_additional_properties_true_strict_allows_extra(self):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": True,
        }
        spec = SchemaPath.from_dict(schema)
        value = {
            "name": "openapi-core",
            "extra": "explicitly allowed",
        }

        result = oas30_write_schema_validators_factory.create(
            spec,
            strict_additional_properties=True,
        ).validate(value)

        assert result is None

    def test_enforce_properties_required_rejects_missing_property(self):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            oas30_write_schema_validators_factory.create(
                spec,
                enforce_properties_required=True,
            ).validate({"name": "openapi-core"})

    def test_enforce_properties_required_ignores_write_only_fields(self):
        schema = {
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
        spec = SchemaPath.from_dict(schema)

        result = oas30_write_schema_validators_factory.create(
            spec,
            enforce_properties_required=True,
        ).validate({"name": "openapi-core"})

        assert result is None

    def test_enforce_properties_required_applies_to_nested_composed_schemas(
        self,
    ):
        schema = {
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
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            oas30_write_schema_validators_factory.create(
                spec,
                enforce_properties_required=True,
            ).validate({"name": "openapi-core", "meta": {}})
