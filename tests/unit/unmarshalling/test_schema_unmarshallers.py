from functools import partial

import pytest
from openapi_schema_validator import OAS30WriteValidator

from openapi_core.spec.paths import Spec
from openapi_core.unmarshalling.schemas import oas30_types_unmarshaller
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.exceptions import FormatUnmarshalError
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory
from openapi_core.validation.schemas.formatters import Formatter


@pytest.fixture
def schema_unmarshaller_factory():
    def create_unmarshaller(
        validators_factory,
        schema,
        format_validators=None,
        extra_format_validators=None,
        extra_format_unmarshallers=None,
        custom_formatters=None,
    ):
        return SchemaUnmarshallersFactory(
            validators_factory,
            oas30_types_unmarshaller,
            custom_formatters=custom_formatters,
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
    def test_schema_custom_formatter_format_invalid(
        self, unmarshaller_factory
    ):
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
        with pytest.warns(DeprecationWarning):
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
        with pytest.warns(DeprecationWarning):
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
        with pytest.warns(DeprecationWarning):
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
        with pytest.warns(DeprecationWarning):
            unmarshaller = unmarshaller_factory(
                spec, custom_formatters=custom_formatters
            )

        with pytest.raises(FormatUnmarshalError):
            unmarshaller.unmarshal(value)

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
        spec = Spec.from_dict(schema, validator=None)
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

        with pytest.raises(FormatUnmarshalError):
            unmarshaller.unmarshal(value)

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
        spec = Spec.from_dict(schema, validator=None)
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
        spec = Spec.from_dict(schema, validator=None)
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
        spec = Spec.from_dict(schema, validator=None)
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
        )
    )
    def test_schema_format_validator_format_invalid(
        self, schema_unmarshaller_factory, unmarshaller_factory
    ):
        custom_format = "date"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema, validator=None)
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
        spec = Spec.from_dict(schema, validator=None)
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
