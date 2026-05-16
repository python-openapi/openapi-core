from functools import partial

import pytest
from jsonschema_path import SchemaPath
from openapi_schema_validator import OAS30WriteValidator

from openapi_core.unmarshalling.schemas import oas30_types_unmarshaller
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.unmarshallers import SchemaUnmarshaller
from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory
from openapi_core.validation.schemas.validators import SchemaValidator


@pytest.fixture
def spec():
    spec_dict = {}
    return SchemaPath.from_dict(spec_dict)


@pytest.fixture
def schema_unmarshaller_factory(spec):
    def create_unmarshaller(
        validators_factory,
        schema,
        format_validators=None,
        extra_format_validators=None,
        extra_format_unmarshallers=None,
    ):
        return SchemaUnmarshallersFactory(
            validators_factory,
            oas30_types_unmarshaller,
        ).create(
            spec,
            schema,
            format_validators=format_validators,
            extra_format_validators=extra_format_validators,
            extra_format_unmarshallers=extra_format_unmarshallers,
        )

    return create_unmarshaller


@pytest.fixture
def unmarshaller_factory(schema_unmarshaller_factory):
    return partial(
        schema_unmarshaller_factory,
        oas30_write_schema_validators_factory,
    )


class TestOAS30SchemaUnmarshallerFactoryCreate:
    def test_string_format_unknown(self, unmarshaller_factory):
        unknown_format = "unknown"
        schema = {
            "type": "string",
            "format": unknown_format,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(FormatterNotFoundError):
            unmarshaller_factory(spec)

    def test_string_format_invalid_value(self, unmarshaller_factory):
        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(
            FormatterNotFoundError,
            match="Formatter not found for custom format",
        ):
            unmarshaller_factory(spec)


class TestOAS30SchemaUnmarshallerUnmarshal:
    def test_schema_extra_format_unmarshaller_format_invalid(
        self, schema_unmarshaller_factory, unmarshaller_factory
    ):
        def custom_format_unmarshaller(value):
            raise ValueError

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": "custom",
        }
        spec = SchemaPath.from_dict(schema)
        value = "x"
        schema_validators_factory = SchemaValidatorsFactory(
            OAS30WriteValidator
        )
        extra_format_unmarshallers = {
            custom_format: custom_format_unmarshaller,
        }
        unmarshaller = schema_unmarshaller_factory(
            schema_validators_factory,
            spec,
            extra_format_unmarshallers=extra_format_unmarshallers,
        )

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_schema_extra_format_unmarshaller_format_custom(
        self, schema_unmarshaller_factory
    ):
        formatted = "x-custom"

        def custom_format_unmarshaller(value):
            return formatted

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = SchemaPath.from_dict(schema)
        value = "x"
        schema_validators_factory = SchemaValidatorsFactory(
            OAS30WriteValidator
        )
        extra_format_unmarshallers = {
            custom_format: custom_format_unmarshaller,
        }
        unmarshaller = schema_unmarshaller_factory(
            schema_validators_factory,
            spec,
            extra_format_unmarshallers=extra_format_unmarshallers,
        )

        result = unmarshaller.unmarshal(value)

        assert result == formatted

    def test_schema_extra_format_validator_format_invalid(
        self, schema_unmarshaller_factory, unmarshaller_factory
    ):
        def custom_format_validator(value):
            return False

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = SchemaPath.from_dict(schema)
        value = "x"
        schema_validators_factory = SchemaValidatorsFactory(
            OAS30WriteValidator
        )
        extra_format_validators = {
            custom_format: custom_format_validator,
        }
        unmarshaller = schema_unmarshaller_factory(
            schema_validators_factory,
            spec,
            extra_format_validators=extra_format_validators,
        )

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    def test_schema_extra_format_validator_format_custom(
        self, schema_unmarshaller_factory
    ):
        def custom_format_validator(value):
            return True

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = SchemaPath.from_dict(schema)
        value = "x"
        schema_validators_factory = SchemaValidatorsFactory(
            OAS30WriteValidator
        )
        extra_format_validators = {
            custom_format: custom_format_validator,
        }
        unmarshaller = schema_unmarshaller_factory(
            schema_validators_factory,
            spec,
            extra_format_validators=extra_format_validators,
        )

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.xfail(
        reason=(
            "Not registered format raises FormatterNotFoundError"
            "See https://github.com/python-openapi/openapi-core/issues/515"
        ),
        strict=True,
    )
    def test_schema_format_validator_format_invalid(
        self, schema_unmarshaller_factory, unmarshaller_factory
    ):
        custom_format = "date"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = SchemaPath.from_dict(schema)
        value = "x"
        schema_validators_factory = SchemaValidatorsFactory(
            OAS30WriteValidator
        )
        format_validators = {}
        unmarshaller = schema_unmarshaller_factory(
            schema_validators_factory,
            spec,
            format_validators=format_validators,
        )

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_schema_format_validator_format_custom(
        self, schema_unmarshaller_factory, unmarshaller_factory
    ):
        def custom_format_validator(value):
            return True

        custom_format = "date"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = SchemaPath.from_dict(schema)
        value = "x"
        schema_validators_factory = SchemaValidatorsFactory(
            OAS30WriteValidator
        )
        format_validators = {
            custom_format: custom_format_validator,
        }
        unmarshaller = schema_unmarshaller_factory(
            schema_validators_factory,
            spec,
            format_validators=format_validators,
        )

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_unmarshal_state_skips_repeat_validation(
        self,
        schema_unmarshaller_factory,
    ):
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "integer"},
                }
            },
        }
        spec = SchemaPath.from_dict(schema)
        value = {"items": [1, 2, 3]}
        unmarshaller = schema_unmarshaller_factory(
            oas30_write_schema_validators_factory,
            spec,
        )
        assert isinstance(unmarshaller, SchemaUnmarshaller)

        validate_state_spy = pytest.MonkeyPatch()
        calls = []
        original_validate_state = unmarshaller.schema_validator.validate_state

        def spy_validate_state(inner_value):
            calls.append(inner_value)
            return original_validate_state(inner_value)

        validate_state_spy.setattr(
            unmarshaller.schema_validator,
            "validate_state",
            spy_validate_state,
        )
        try:
            state = original_validate_state(value)
            result = unmarshaller.unmarshal_state(state)
        finally:
            validate_state_spy.undo()

        assert result == {"items": [1, 2, 3]}
        assert calls == []

    def test_unmarshal_state_reuses_composed_schema_selection_for_properties(
        self,
        schema_unmarshaller_factory,
        monkeypatch,
    ):
        schema = {
            "type": "object",
            "oneOf": [
                {
                    "type": "object",
                    "required": ["kind", "created_at"],
                    "properties": {
                        "kind": {"type": "string"},
                        "created_at": {
                            "type": "string",
                            "format": "date",
                        },
                    },
                },
                {
                    "type": "object",
                    "required": ["kind", "count"],
                    "properties": {
                        "kind": {"type": "string"},
                        "count": {"type": "integer"},
                    },
                },
            ],
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                    },
                }
            ],
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                    },
                }
            ],
        }
        spec = SchemaPath.from_dict(schema)
        value = {
            "kind": "counted",
            "count": 3,
        }
        unmarshaller = schema_unmarshaller_factory(
            oas30_write_schema_validators_factory,
            spec,
        )
        assert isinstance(unmarshaller, SchemaUnmarshaller)

        state = unmarshaller.schema_validator.validate_state(value)

        monkeypatch.setattr(
            SchemaValidator,
            "get_one_of_schema",
            lambda self, value, caster=None: (_ for _ in ()).throw(
                AssertionError("oneOf recomputed during unmarshal_state")
            ),
        )
        monkeypatch.setattr(
            SchemaValidator,
            "iter_any_of_schemas",
            lambda self, value, caster=None: (_ for _ in ()).throw(
                AssertionError("anyOf recomputed during unmarshal_state")
            ),
        )
        monkeypatch.setattr(
            SchemaValidator,
            "iter_all_of_schemas",
            lambda self, value: (_ for _ in ()).throw(
                AssertionError("allOf recomputed during unmarshal_state")
            ),
        )

        result = unmarshaller.unmarshal_state(state)

        assert result == {"kind": "counted", "count": 3}

    def test_unmarshal_state_reuses_composed_schema_selection_for_format(
        self,
        schema_unmarshaller_factory,
        monkeypatch,
    ):
        schema = {
            "oneOf": [
                {"type": "integer"},
                {
                    "type": "string",
                    "format": "date",
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        value = "2018-01-02"
        unmarshaller = schema_unmarshaller_factory(
            oas30_write_schema_validators_factory,
            spec,
        )
        assert isinstance(unmarshaller, SchemaUnmarshaller)

        state = unmarshaller.schema_validator.validate_state(value)

        monkeypatch.setattr(
            SchemaValidator,
            "iter_valid_schemas",
            lambda self, value: (_ for _ in ()).throw(
                AssertionError(
                    "valid schemas recomputed during unmarshal_state"
                )
            ),
        )

        result = unmarshaller.unmarshal_state(state)

        assert result == value

    def test_unmarshal_state_reuses_additional_properties_state(
        self,
        schema_unmarshaller_factory,
        monkeypatch,
    ):
        schema = {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
        }
        spec = SchemaPath.from_dict(schema)
        value = {
            "extras": [{"a": 1}, {"b": 2}],
        }
        unmarshaller = schema_unmarshaller_factory(
            oas30_write_schema_validators_factory,
            spec,
        )
        assert isinstance(unmarshaller, SchemaUnmarshaller)

        state = unmarshaller.schema_validator.validate_state(value)

        monkeypatch.setattr(
            SchemaValidator,
            "validate_state",
            lambda self, value: (_ for _ in ()).throw(
                AssertionError(
                    "additionalProperties revalidated during unmarshal_state"
                )
            ),
        )

        result = unmarshaller.unmarshal_state(state)

        assert result == value

    def test_validate_state_only_checks_composed_schemas_where_declared(
        self,
        schema_unmarshaller_factory,
        monkeypatch,
    ):
        schema = {
            "type": "object",
            "oneOf": [
                {
                    "type": "object",
                    "required": ["kind", "payload"],
                    "properties": {
                        "kind": {"type": "string"},
                        "payload": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "type": "object",
                                    "required": ["count"],
                                    "properties": {
                                        "count": {"type": "integer"},
                                    },
                                },
                                {
                                    "type": "object",
                                    "required": ["label"],
                                    "properties": {
                                        "label": {"type": "string"},
                                    },
                                },
                            ],
                        },
                    },
                }
            ],
        }
        spec = SchemaPath.from_dict(schema)
        value = {
            "kind": "counted",
            "payload": {"count": 3},
        }
        unmarshaller = schema_unmarshaller_factory(
            oas30_write_schema_validators_factory,
            spec,
        )
        assert isinstance(unmarshaller, SchemaUnmarshaller)

        original_get_one_of_schema = SchemaValidator.get_one_of_schema
        calls = []

        def spy_get_one_of_schema(self, inner_value, caster=None):
            calls.append(inner_value)
            return original_get_one_of_schema(self, inner_value, caster=caster)

        monkeypatch.setattr(
            SchemaValidator,
            "get_one_of_schema",
            spy_get_one_of_schema,
        )

        state = unmarshaller.schema_validator.validate_state(value)

        assert state.one_of_state is not None
        assert calls == [
            {"kind": "counted", "payload": {"count": 3}},
            {"count": 3},
        ]
