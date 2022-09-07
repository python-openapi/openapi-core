import datetime
import uuid

import pytest
from isodate.tzinfo import UTC
from isodate.tzinfo import FixedOffset
from openapi_schema_validator import OAS30Validator

from openapi_core.spec.paths import Spec
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.exceptions import (
    InvalidSchemaFormatValue,
)
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.unmarshalling.schemas.exceptions import UnmarshalError
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter


@pytest.fixture
def unmarshaller_factory():
    def create_unmarshaller(
        schema, custom_formatters=None, context=UnmarshalContext.REQUEST
    ):
        custom_formatters = custom_formatters or {}
        return SchemaUnmarshallersFactory(
            OAS30Validator,
            custom_formatters=custom_formatters,
            context=context,
        ).create(schema)

    return create_unmarshaller


class TestUnmarshal:
    def test_no_schema(self, unmarshaller_factory):
        spec = None
        value = "test"

        with pytest.raises(TypeError):
            unmarshaller_factory(spec).unmarshal(value)

    def test_schema_type_invalid(self, unmarshaller_factory):
        schema = {
            "type": "integer",
        }
        spec = Spec.from_dict(schema)
        value = "test"

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(spec).unmarshal(value)

    def test_schema_custom_format_invalid(self, unmarshaller_factory):
        class CustomFormatter(Formatter):
            def unmarshal(self, value):
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
        spec = Spec.from_dict(schema)
        value = "test"

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(
                spec,
                custom_formatters=custom_formatters,
            ).unmarshal(value)


class TestSchemaUnmarshallerCall:
    def test_deprecated(self, unmarshaller_factory):
        schema = {
            "type": "string",
            "deprecated": True,
        }
        spec = Spec.from_dict(schema)
        value = "test"

        with pytest.warns(DeprecationWarning):
            result = unmarshaller_factory(spec)(value)

        assert result == value

    @pytest.mark.parametrize(
        "schema_type",
        [
            "boolean",
            "array",
            "integer",
            "number",
        ],
    )
    def test_non_string_empty_value(self, schema_type, unmarshaller_factory):
        schema = {
            "type": schema_type,
        }
        spec = Spec.from_dict(schema)
        value = ""

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_string_valid(self, unmarshaller_factory):
        schema = {
            "type": "string",
        }
        spec = Spec.from_dict(schema)
        value = "test"

        result = unmarshaller_factory(spec)(value)

        assert result == value

    def test_string_format_uuid_valid(self, unmarshaller_factory):
        schema = {
            "type": "string",
            "format": "uuid",
        }
        spec = Spec.from_dict(schema)
        value = str(uuid.uuid4())

        result = unmarshaller_factory(spec)(value)

        assert result == uuid.UUID(value)

    def test_string_format_uuid_uuid_quirks_invalid(
        self, unmarshaller_factory
    ):
        schema = {
            "type": "string",
            "format": "uuid",
        }
        spec = Spec.from_dict(schema)
        value = uuid.uuid4()

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_string_format_password(self, unmarshaller_factory):
        schema = {
            "type": "string",
            "format": "password",
        }
        spec = Spec.from_dict(schema)
        value = "password"

        result = unmarshaller_factory(spec)(value)

        assert result == "password"

    def test_string_float_invalid(self, unmarshaller_factory):
        schema = {
            "type": "string",
        }
        spec = Spec.from_dict(schema)
        value = 1.23

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_string_format_date(self, unmarshaller_factory):
        schema = {
            "type": "string",
            "format": "date",
        }
        spec = Spec.from_dict(schema)
        value = "2018-01-02"

        result = unmarshaller_factory(spec)(value)

        assert result == datetime.date(2018, 1, 2)

    def test_string_format_datetime_invalid(self, unmarshaller_factory):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = Spec.from_dict(schema)
        value = "2018-01-02T00:00:00"

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_string_format_datetime_utc(self, unmarshaller_factory):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = Spec.from_dict(schema)
        value = "2018-01-02T00:00:00Z"

        result = unmarshaller_factory(spec)(value)

        tzinfo = UTC
        assert result == datetime.datetime(2018, 1, 2, 0, 0, tzinfo=tzinfo)

    def test_string_format_datetime_tz(self, unmarshaller_factory):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = Spec.from_dict(schema)
        value = "2020-04-01T12:00:00+02:00"

        result = unmarshaller_factory(spec)(value)

        tzinfo = FixedOffset(2)
        assert result == datetime.datetime(2020, 4, 1, 12, 0, 0, tzinfo=tzinfo)

    def test_string_format_custom(self, unmarshaller_factory):
        formatted = "x-custom"

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                return formatted

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema)
        value = "x"
        formatter = CustomFormatter()
        custom_formatters = {
            custom_format: formatter,
        }

        result = unmarshaller_factory(
            spec, custom_formatters=custom_formatters
        )(value)

        assert result == formatted

    def test_string_format_custom_value_error(self, unmarshaller_factory):
        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                raise ValueError

        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema)
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
        spec = Spec.from_dict(schema)
        value = "x"

        with pytest.raises(FormatterNotFoundError):
            unmarshaller_factory(spec)(value)

    def test_string_format_invalid_value(self, unmarshaller_factory):
        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema)
        value = "x"

        with pytest.raises(
            FormatterNotFoundError,
            match="Formatter not found for custom format",
        ):
            unmarshaller_factory(spec)(value)

    def test_integer_valid(self, unmarshaller_factory):
        schema = {
            "type": "integer",
        }
        spec = Spec.from_dict(schema)
        value = 123

        result = unmarshaller_factory(spec)(value)

        assert result == int(value)

    def test_integer_string_invalid(self, unmarshaller_factory):
        schema = {
            "type": "integer",
        }
        spec = Spec.from_dict(schema)
        value = "123"

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_integer_enum_invalid(self, unmarshaller_factory):
        schema = {
            "type": "integer",
            "enum": [1, 2, 3],
        }
        spec = Spec.from_dict(schema)
        value = "123"

        with pytest.raises(UnmarshalError):
            unmarshaller_factory(spec)(value)

    def test_integer_enum(self, unmarshaller_factory):
        schema = {
            "type": "integer",
            "enum": [1, 2, 3],
        }
        spec = Spec.from_dict(schema)
        value = 2

        result = unmarshaller_factory(spec)(value)

        assert result == int(value)

    def test_integer_enum_string_invalid(self, unmarshaller_factory):
        schema = {
            "type": "integer",
            "enum": [1, 2, 3],
        }
        spec = Spec.from_dict(schema)
        value = "2"

        with pytest.raises(UnmarshalError):
            unmarshaller_factory(spec)(value)

    def test_integer_default_nullable(self, unmarshaller_factory):
        default_value = 123
        schema = {
            "type": "integer",
            "default": default_value,
            "nullable": True,
        }
        spec = Spec.from_dict(schema)
        value = None

        result = unmarshaller_factory(spec)(value)

        assert result is None

    def test_integer_invalid(self, unmarshaller_factory):
        schema = {
            "type": "integer",
        }
        spec = Spec.from_dict(schema)
        value = "abc"

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_array_valid(self, unmarshaller_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "integer",
            },
        }
        spec = Spec.from_dict(schema)
        value = [1, 2, 3]

        result = unmarshaller_factory(spec)(value)

        assert result == value

    def test_array_null(self, unmarshaller_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "integer",
            },
        }
        spec = Spec.from_dict(schema)
        value = None

        with pytest.raises(TypeError):
            unmarshaller_factory(spec)(value)

    def test_array_nullable(self, unmarshaller_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "integer",
            },
            "nullable": True,
        }
        spec = Spec.from_dict(schema)
        value = None
        result = unmarshaller_factory(spec)(value)

        assert result is None

    def test_array_of_string_string_invalid(self, unmarshaller_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "string",
            },
        }
        spec = Spec.from_dict(schema)
        value = "123"

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_array_of_integer_string_invalid(self, unmarshaller_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "integer",
            },
        }
        spec = Spec.from_dict(schema)
        value = "123"

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_boolean_valid(self, unmarshaller_factory):
        schema = {
            "type": "boolean",
        }
        spec = Spec.from_dict(schema)
        value = True

        result = unmarshaller_factory(spec)(value)

        assert result == value

    def test_boolean_string_invalid(self, unmarshaller_factory):
        schema = {
            "type": "boolean",
        }
        spec = Spec.from_dict(schema)
        value = "True"

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_number_valid(self, unmarshaller_factory):
        schema = {
            "type": "number",
        }
        spec = Spec.from_dict(schema)
        value = 1.23

        result = unmarshaller_factory(spec)(value)

        assert result == value

    def test_number_string_invalid(self, unmarshaller_factory):
        schema = {
            "type": "number",
        }
        spec = Spec.from_dict(schema)
        value = "1.23"

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_number_int(self, unmarshaller_factory):
        schema = {
            "type": "number",
        }
        spec = Spec.from_dict(schema)
        value = 1
        result = unmarshaller_factory(spec)(value)

        assert result == 1
        assert type(result) == int

    def test_number_float(self, unmarshaller_factory):
        schema = {
            "type": "number",
        }
        spec = Spec.from_dict(schema)
        value = 1.2
        result = unmarshaller_factory(spec)(value)

        assert result == 1.2
        assert type(result) == float

    def test_number_format_float(self, unmarshaller_factory):
        schema = {
            "type": "number",
            "format": "float",
        }
        spec = Spec.from_dict(schema)
        value = 1.2
        result = unmarshaller_factory(spec)(value)

        assert result == 1.2

    def test_number_format_double(self, unmarshaller_factory):
        schema = {
            "type": "number",
            "format": "double",
        }
        spec = Spec.from_dict(schema)
        value = 1.2
        result = unmarshaller_factory(spec)(value)

        assert result == 1.2

    def test_object_nullable(self, unmarshaller_factory):
        schema = {
            "type": "object",
            "properties": {
                "foo": {
                    "type": "object",
                    "nullable": True,
                }
            },
        }
        spec = Spec.from_dict(schema)
        value = {"foo": None}
        result = unmarshaller_factory(spec)(value)

        assert result == {"foo": None}

    def test_schema_any_one_of(self, unmarshaller_factory):
        schema = {
            "oneOf": [
                {
                    "type": "string",
                },
                {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            ],
        }
        spec = Spec.from_dict(schema)
        assert unmarshaller_factory(spec)(["hello"]) == ["hello"]

    def test_schema_any_all_of(self, unmarshaller_factory):
        schema = {
            "allOf": [
                {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                }
            ],
        }
        spec = Spec.from_dict(schema)
        assert unmarshaller_factory(spec)(["hello"]) == ["hello"]

    @pytest.mark.parametrize(
        "value",
        [
            {
                "somestr": {},
                "someint": 123,
            },
            {
                "somestr": ["content1", "content2"],
                "someint": 123,
            },
            {
                "somestr": 123,
                "someint": 123,
            },
            {
                "somestr": "content",
                "someint": 123,
                "not_in_scheme_prop": 123,
            },
        ],
    )
    def test_schema_any_all_of_invalid_properties(
        self, value, unmarshaller_factory
    ):
        schema = {
            "allOf": [
                {
                    "type": "object",
                    "required": ["somestr"],
                    "properties": {
                        "somestr": {
                            "type": "string",
                        },
                    },
                },
                {
                    "type": "object",
                    "required": ["someint"],
                    "properties": {
                        "someint": {
                            "type": "integer",
                        },
                    },
                },
            ],
            "additionalProperties": False,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec)(value)

    def test_schema_any_all_of_any(self, unmarshaller_factory):
        schema = {
            "allOf": [
                {},
                {
                    "type": "string",
                    "format": "date",
                },
            ],
        }
        spec = Spec.from_dict(schema)
        value = "2018-01-02"

        result = unmarshaller_factory(spec)(value)

        assert result == datetime.date(2018, 1, 2)

    def test_schema_any(self, unmarshaller_factory):
        schema = {}
        spec = Spec.from_dict(schema)
        assert unmarshaller_factory(spec)("string") == "string"

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
            {"foo": "bar", "bar": "foo"},
            {"additional": {"bar": 1}},
        ],
    )
    @pytest.mark.parametrize("additional_properties", [True, {}])
    def test_schema_free_form_object(
        self, value, additional_properties, unmarshaller_factory
    ):
        schema = {
            "type": "object",
            "additionalProperties": additional_properties,
        }
        spec = Spec.from_dict(schema)

        result = unmarshaller_factory(spec)(value)
        assert result == value

    def test_read_only_properties(self, unmarshaller_factory):
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {
                    "type": "integer",
                    "readOnly": True,
                }
            },
        }
        spec = Spec.from_dict(schema)

        # readOnly properties may be admitted in a Response context
        result = unmarshaller_factory(spec, context=UnmarshalContext.RESPONSE)(
            {"id": 10}
        )
        assert result == {
            "id": 10,
        }

    def test_read_only_properties_invalid(self, unmarshaller_factory):
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {
                    "type": "integer",
                    "readOnly": True,
                }
            },
        }
        spec = Spec.from_dict(schema)

        # readOnly properties are not admitted on a Request context
        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec, context=UnmarshalContext.REQUEST)(
                {"id": 10}
            )

    def test_write_only_properties(self, unmarshaller_factory):
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {
                    "type": "integer",
                    "writeOnly": True,
                }
            },
        }
        spec = Spec.from_dict(schema)

        # readOnly properties may be admitted in a Response context
        result = unmarshaller_factory(spec, context=UnmarshalContext.REQUEST)(
            {"id": 10}
        )
        assert result == {
            "id": 10,
        }

    def test_write_only_properties_invalid(self, unmarshaller_factory):
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {
                    "type": "integer",
                    "writeOnly": True,
                }
            },
        }
        spec = Spec.from_dict(schema)

        # readOnly properties are not admitted on a Request context
        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(spec, context=UnmarshalContext.RESPONSE)(
                {"id": 10}
            )
