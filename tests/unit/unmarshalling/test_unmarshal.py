from functools import partial

import pytest
from openapi_schema_validator import OAS30Validator

from openapi_core.spec.paths import Spec
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.exceptions import (
    InvalidSchemaFormatValue,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter


@pytest.fixture
def schema_unmarshaller_factory():
    def create_unmarshaller(
        validator, schema, custom_formatters=None, context=None
    ):
        custom_formatters = custom_formatters or {}
        return SchemaUnmarshallersFactory(
            validator,
            custom_formatters=custom_formatters,
            context=context,
        ).create(schema)

    return create_unmarshaller


class TestOAS30SchemaUnmarshallerUnmarshal:
    @pytest.fixture
    def unmarshaller_factory(self, schema_unmarshaller_factory):
        return partial(schema_unmarshaller_factory, OAS30Validator)

    def test_schema_custom_format_invalid(self, unmarshaller_factory):
        class CustomFormatter(Formatter):
            def format(self, value):
                raise ValueError

        formatter = CustomFormatter()
        custom_format = "custom"
        custom_formatters = {
            custom_format: formatter,
        }
        schema = {
            "type": "string",
            "format": "custom",
        }
        spec = Spec.from_dict(schema, validator=None)
        value = "test"

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(
                spec,
                custom_formatters=custom_formatters,
            ).unmarshal(value)


class TestOAS30SchemaUnmarshallerCall:
    @pytest.fixture
    def unmarshaller_factory(self, schema_unmarshaller_factory):
        return partial(schema_unmarshaller_factory, OAS30Validator)

    def test_string_format_custom(self, unmarshaller_factory):
        formatted = "x-custom"

        class CustomFormatter(Formatter):
            def format(self, value):
                return formatted

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema, validator=None)
        value = "x"
        formatter = CustomFormatter()
        custom_formatters = {
            custom_format: formatter,
        }

        result = unmarshaller_factory(
            spec, custom_formatters=custom_formatters
        )(value)

        assert result == formatted

    def test_string_format_custom_formatter(self, unmarshaller_factory):
        formatted = "x-custom"

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                return formatted

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema, validator=None)
        value = "x"
        formatter = CustomFormatter()
        custom_formatters = {
            custom_format: formatter,
        }

        with pytest.warns(DeprecationWarning):
            result = unmarshaller_factory(
                spec, custom_formatters=custom_formatters
            )(value)

        assert result == formatted

    def test_string_format_custom_value_error(self, unmarshaller_factory):
        class CustomFormatter(Formatter):
            def format(self, value):
                raise ValueError

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema, validator=None)
        value = "x"
        formatter = CustomFormatter()
        custom_formatters = {
            custom_format: formatter,
        }

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(spec, custom_formatters=custom_formatters)(
                value
            )

    def test_string_format_unknown(self, unmarshaller_factory):
        unknown_format = "unknown"
        schema = {
            "type": "string",
            "format": unknown_format,
        }
        spec = Spec.from_dict(schema, validator=None)
        value = "x"

        with pytest.raises(FormatterNotFoundError):
            unmarshaller_factory(spec)(value)

    def test_string_format_invalid_value(self, unmarshaller_factory):
        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema, validator=None)
        value = "x"

        with pytest.raises(
            FormatterNotFoundError,
            match="Formatter not found for custom format",
        ):
            unmarshaller_factory(spec)(value)
