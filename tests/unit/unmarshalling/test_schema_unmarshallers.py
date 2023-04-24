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
from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory


@pytest.fixture
def schema_unmarshaller_factory():
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
