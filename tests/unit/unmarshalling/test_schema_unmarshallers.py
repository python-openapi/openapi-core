from functools import partial

import pytest

from openapi_core.spec.paths import Spec
from openapi_core.unmarshalling.schemas import oas30_types_unmarshaller
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.exceptions import FormatUnmarshalError
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)


@pytest.fixture
def schema_unmarshaller_factory():
    def create_unmarshaller(
        validators_factory, schema, custom_formatters=None
    ):
        custom_formatters = custom_formatters or {}
        return SchemaUnmarshallersFactory(
            validators_factory,
            oas30_types_unmarshaller,
            custom_formatters=custom_formatters,
        ).create(schema)

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
        spec = Spec.from_dict(schema, validator=None)

        with pytest.raises(FormatterNotFoundError):
            unmarshaller_factory(spec)

    def test_string_format_invalid_value(self, unmarshaller_factory):
        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema, validator=None)

        with pytest.raises(
            FormatterNotFoundError,
            match="Formatter not found for custom format",
        ):
            unmarshaller_factory(spec)


class TestOAS30SchemaUnmarshallerUnmarshal:
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
        value = "x"
        unmarshaller = unmarshaller_factory(
            spec,
            custom_formatters=custom_formatters,
        )

        with pytest.raises(FormatUnmarshalError):
            unmarshaller.unmarshal(value)

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
        unmarshaller = unmarshaller_factory(
            spec, custom_formatters=custom_formatters
        )

        result = unmarshaller.unmarshal(value)

        assert result == formatted

    def test_array_format_custom_formatter(self, unmarshaller_factory):
        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                return tuple(value)

        custom_format = "custom"
        schema = {
            "type": "array",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema, validator=None)
        value = ["x"]
        formatter = CustomFormatter()
        custom_formatters = {
            custom_format: formatter,
        }
        unmarshaller = unmarshaller_factory(
            spec, custom_formatters=custom_formatters
        )

        with pytest.warns(DeprecationWarning):
            result = unmarshaller.unmarshal(value)

        assert result == tuple(value)

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
        unmarshaller = unmarshaller_factory(
            spec, custom_formatters=custom_formatters
        )

        with pytest.raises(FormatUnmarshalError):
            unmarshaller.unmarshal(value)
