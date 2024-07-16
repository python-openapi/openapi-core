from datetime import date
from datetime import datetime
from uuid import UUID
from uuid import uuid4

import pytest
from isodate.tzinfo import UTC
from isodate.tzinfo import FixedOffset
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import UnknownType
from jsonschema_path import SchemaPath

from openapi_core.unmarshalling.schemas import (
    oas30_read_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas30_write_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue


class BaseTestOASSchemaUnmarshallersFactoryCall:
    def test_create_no_schema(self, unmarshallers_factory):
        with pytest.raises(TypeError):
            unmarshallers_factory.create(None)

    def test_create_schema_deprecated(self, unmarshallers_factory):
        schema = {
            "deprecated": True,
        }
        spec = SchemaPath.from_dict(schema)
        with pytest.warns(DeprecationWarning):
            unmarshallers_factory.create(spec)

    def test_create_formatter_not_found(self, unmarshallers_factory):
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
            unmarshallers_factory.create(spec)

    @pytest.mark.parametrize(
        "value",
        [
            "test",
            10,
            10,
            3.12,
            ["one", "two"],
            True,
            False,
        ],
    )
    def test_no_type(self, unmarshallers_factory, value):
        schema = {}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "type,value",
        [
            ("string", "test"),
            ("integer", 10),
            ("number", 10),
            ("number", 3.12),
            ("array", ["one", "two"]),
            ("boolean", True),
            ("boolean", False),
        ],
    )
    def test_basic_types(self, unmarshallers_factory, type, value):
        schema = {
            "type": type,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "type,value",
        [
            ("string", 10),
            ("string", 3.14),
            ("string", True),
            ("string", ["one", "two"]),
            ("string", {"one": "two"}),
            ("integer", 3.14),
            ("integer", True),
            ("integer", ""),
            ("integer", "test"),
            ("integer", b"test"),
            ("integer", ["one", "two"]),
            ("integer", {"one": "two"}),
            ("number", True),
            ("number", ""),
            ("number", "test"),
            ("number", b"test"),
            ("number", ["one", "two"]),
            ("number", {"one": "two"}),
            ("array", 10),
            ("array", 3.14),
            ("array", True),
            ("array", ""),
            ("array", "test"),
            ("array", b"test"),
            ("array", {"one": "two"}),
            ("boolean", 10),
            ("boolean", 3.14),
            ("boolean", ""),
            ("boolean", "test"),
            ("boolean", b"test"),
            ("boolean", ["one", "two"]),
            ("boolean", {"one": "two"}),
            ("object", 10),
            ("object", 3.14),
            ("object", True),
            ("object", ""),
            ("object", "test"),
            ("object", b"test"),
            ("object", ["one", "two"]),
        ],
    )
    def test_basic_types_invalid(self, unmarshallers_factory, type, value):
        schema = {
            "type": type,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(
            InvalidSchemaValue,
            match=f"not valid for schema of type {type}",
        ) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"is not of type '{type}'"
            in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize(
        "format,value,unmarshalled",
        [
            ("int32", 13, 13),
            ("int64", 13, 13),
            ("float", 3.14, 3.14),
            ("double", 3.14, 3.14),
            ("password", "passwd", "passwd"),
            ("date", "2018-12-13", date(2018, 12, 13)),
            (
                "date-time",
                "2018-12-13T13:34:59Z",
                datetime(2018, 12, 13, 13, 34, 59, tzinfo=UTC),
            ),
            (
                "date-time",
                "2018-12-13T13:34:59+02:00",
                datetime(2018, 12, 13, 13, 34, 59, tzinfo=FixedOffset(2)),
            ),
            (
                "uuid",
                "20a53f2e-0049-463d-b2b4-3fbbbb4cd8a7",
                UUID("20a53f2e-0049-463d-b2b4-3fbbbb4cd8a7"),
            ),
        ],
    )
    def test_basic_formats(
        self, unmarshallers_factory, format, value, unmarshalled
    ):
        schema = {
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == unmarshalled

    @pytest.mark.parametrize(
        "type,format,value,unmarshalled",
        [
            ("integer", "int32", 13, 13),
            ("integer", "int64", 13, 13),
            ("number", "float", 3.14, 3.14),
            ("number", "double", 3.14, 3.14),
            ("string", "password", "passwd", "passwd"),
            ("string", "date", "2018-12-13", date(2018, 12, 13)),
            (
                "string",
                "date-time",
                "2018-12-13T13:34:59Z",
                datetime(2018, 12, 13, 13, 34, 59, tzinfo=UTC),
            ),
            (
                "string",
                "date-time",
                "2018-12-13T13:34:59+02:00",
                datetime(2018, 12, 13, 13, 34, 59, tzinfo=FixedOffset(2)),
            ),
            (
                "string",
                "uuid",
                "20a53f2e-0049-463d-b2b4-3fbbbb4cd8a7",
                UUID("20a53f2e-0049-463d-b2b4-3fbbbb4cd8a7"),
            ),
        ],
    )
    def test_basic_type_formats(
        self, unmarshallers_factory, type, format, value, unmarshalled
    ):
        schema = {
            "type": type,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == unmarshalled

    @pytest.mark.parametrize(
        "type,format,value",
        [
            ("string", "float", "test"),
            ("string", "double", "test"),
            ("number", "date", 3),
            ("number", "date-time", 3),
            ("number", "uuid", 3),
        ],
    )
    def test_basic_type_formats_ignored(
        self, unmarshallers_factory, type, format, value
    ):
        schema = {
            "type": type,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "type,format,value",
        [
            ("string", "date", "test"),
            ("string", "date-time", "test"),
            ("string", "uuid", "test"),
        ],
    )
    def test_basic_type_formats_invalid(
        self, unmarshallers_factory, type, format, value
    ):
        schema = {
            "type": type,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"is not a '{format}'" in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("dGVzdA==", "test"),
        ],
    )
    def test_string_byte(self, unmarshallers_factory, value, expected):
        schema = {
            "type": "string",
            "format": "byte",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == expected

    def test_string_date(self, unmarshallers_factory):
        schema = {
            "type": "string",
            "format": "date",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = "2018-01-02"

        result = unmarshaller.unmarshal(value)

        assert result == date(2018, 1, 2)

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("2018-01-02T00:00:00Z", datetime(2018, 1, 2, 0, 0, tzinfo=UTC)),
            (
                "2020-04-01T12:00:00+02:00",
                datetime(2020, 4, 1, 12, 0, 0, tzinfo=FixedOffset(2)),
            ),
        ],
    )
    def test_string_datetime(self, unmarshallers_factory, value, expected):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == expected

    def test_string_datetime_invalid(self, unmarshallers_factory):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = "2018-01-02T00:00:00"

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            "is not a 'date-time'" in exc_info.value.schema_errors[0].message
        )

    def test_string_password(self, unmarshallers_factory):
        schema = {
            "type": "string",
            "format": "password",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = "passwd"

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_string_uuid(self, unmarshallers_factory):
        schema = {
            "type": "string",
            "format": "uuid",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = str(uuid4())

        result = unmarshaller.unmarshal(value)

        assert result == UUID(value)

    def test_string_uuid_invalid(self, unmarshallers_factory):
        schema = {
            "type": "string",
            "format": "uuid",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = "test"

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert "is not a 'uuid'" in exc_info.value.schema_errors[0].message

    @pytest.mark.parametrize(
        "type,format,value,expected",
        [
            ("string", "float", "test", "test"),
            ("string", "double", "test", "test"),
            ("integer", "byte", 10, 10),
            ("integer", "date", 10, 10),
            ("integer", "date-time", 10, 10),
            ("string", "int32", "test", "test"),
            ("string", "int64", "test", "test"),
            ("integer", "password", 10, 10),
        ],
    )
    def test_formats_ignored(
        self, unmarshallers_factory, type, format, value, expected
    ):
        schema = {
            "type": type,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == expected

    @pytest.mark.parametrize("value", ["bar", "foobar"])
    def test_string_pattern(self, unmarshallers_factory, value):
        schema = {
            "type": "string",
            "pattern": "bar",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value,pattern",
        [
            ("foo", "baz"),
            ("bar", "baz"),
        ],
    )
    def test_string_pattern_invalid(
        self, unmarshallers_factory, value, pattern
    ):
        schema = {
            "type": "string",
            "pattern": pattern,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"'{value}' does not match '{pattern}'"
            in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize("value", ["abc", "abcd"])
    def test_string_min_length(self, unmarshallers_factory, value):
        schema = {
            "type": "string",
            "minLength": 3,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize("value", ["", "a", "ab"])
    def test_string_min_length_invalid(self, unmarshallers_factory, value):
        schema = {
            "type": "string",
            "minLength": 3,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"'{value}' is too short"
            in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize("value", ["", "a"])
    def test_string_max_length(self, unmarshallers_factory, value):
        schema = {
            "type": "string",
            "maxLength": 1,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize("value", ["ab", "abc"])
    def test_string_max_length_invalid(self, unmarshallers_factory, value):
        schema = {
            "type": "string",
            "maxLength": 1,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"'{value}' is too long" in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize(
        "value",
        [
            "",
        ],
    )
    def test_string_max_length_invalid_schema(
        self, unmarshallers_factory, value
    ):
        schema = {
            "type": "string",
            "maxLength": -1,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    def test_integer_enum(self, unmarshallers_factory):
        schema = {
            "type": "integer",
            "enum": [1, 2, 3],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = 2

        result = unmarshaller.unmarshal(value)

        assert result == int(value)

    def test_integer_enum_invalid(self, unmarshallers_factory):
        enum = [1, 2, 3]
        schema = {
            "type": "integer",
            "enum": enum,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = 12

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"{value} is not one of {enum}"
            in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize(
        "type,value",
        [
            ("string", "test"),
            ("integer", 10),
            ("number", 10),
            ("number", 3.12),
            ("array", ["one", "two"]),
            ("boolean", True),
            ("boolean", False),
        ],
    )
    def test_array(self, unmarshallers_factory, type, value):
        schema = {
            "type": "array",
            "items": {
                "type": type,
            },
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value_list = [value] * 3

        result = unmarshaller.unmarshal(value_list)

        assert result == value_list

    @pytest.mark.parametrize(
        "type,value",
        [
            ("integer", True),
            ("integer", "123"),
            ("string", 123),
            ("string", True),
            ("boolean", 123),
            ("boolean", "123"),
        ],
    )
    def test_array_invalid(self, unmarshallers_factory, type, value):
        schema = {
            "type": "array",
            "items": {
                "type": type,
            },
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal([value])
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"is not of type '{type}'"
            in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize("value", [[], [1], [1, 2]])
    def test_array_min_items_invalid(self, unmarshallers_factory, value):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "minItems": 3,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"{value} is too short" in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize("value", [[], [1], [1, 2]])
    def test_array_min_items(self, unmarshallers_factory, value):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "minItems": 0,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            [],
        ],
    )
    def test_array_max_items_invalid_schema(
        self, unmarshallers_factory, value
    ):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "maxItems": -1,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize("value", [[1, 2], [2, 3, 4]])
    def test_array_max_items_invalid(self, unmarshallers_factory, value):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "maxItems": 1,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"{value} is too long" in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize("value", [[1, 2, 1], [2, 2]])
    def test_array_unique_items_invalid(self, unmarshallers_factory, value):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "uniqueItems": True,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"{value} has non-unique elements"
            in exc_info.value.schema_errors[0].message
        )

    def test_object_any_of(self, unmarshallers_factory):
        schema = {
            "type": "object",
            "anyOf": [
                {
                    "type": "object",
                    "required": ["someint"],
                    "properties": {"someint": {"type": "integer"}},
                },
                {
                    "type": "object",
                    "required": ["somestr"],
                    "properties": {"somestr": {"type": "string"}},
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = {"someint": 1}

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_object_any_of_invalid(self, unmarshallers_factory):
        schema = {
            "type": "object",
            "anyOf": [
                {
                    "type": "object",
                    "required": ["someint"],
                    "properties": {"someint": {"type": "integer"}},
                },
                {
                    "type": "object",
                    "required": ["somestr"],
                    "properties": {"somestr": {"type": "string"}},
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal({"someint": "1"})

    def test_object_one_of_default(self, unmarshallers_factory):
        schema = {
            "type": "object",
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "somestr": {
                            "type": "string",
                            "default": "defaultstring",
                        },
                    },
                },
                {
                    "type": "object",
                    "required": ["otherstr"],
                    "properties": {
                        "otherstr": {
                            "type": "string",
                        },
                    },
                },
            ],
            "properties": {
                "someint": {
                    "type": "integer",
                },
            },
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        assert unmarshaller.unmarshal({"someint": 1}) == {
            "someint": 1,
            "somestr": "defaultstring",
        }

    def test_object_any_of_default(self, unmarshallers_factory):
        schema = {
            "type": "object",
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "someint": {
                            "type": "integer",
                        },
                    },
                },
                {
                    "type": "object",
                    "properties": {
                        "somestr": {
                            "type": "string",
                            "default": "defaultstring",
                        },
                    },
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        assert unmarshaller.unmarshal({"someint": "1"}) == {
            "someint": "1",
            "somestr": "defaultstring",
        }

    def test_object_all_of_default(self, unmarshallers_factory):
        schema = {
            "type": "object",
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "somestr": {
                            "type": "string",
                            "default": "defaultstring",
                        },
                    },
                },
                {
                    "type": "object",
                    "properties": {
                        "someint": {
                            "type": "integer",
                            "default": 1,
                        },
                    },
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        assert unmarshaller.unmarshal({}) == {
            "someint": 1,
            "somestr": "defaultstring",
        }

    @pytest.mark.parametrize(
        "value",
        [
            {
                "someint": 123,
            },
            {
                "somestr": "content",
            },
            {
                "somestr": "content",
                "someint": 123,
            },
        ],
    )
    def test_object_with_properties(self, unmarshallers_factory, value):
        schema = {
            "type": "object",
            "properties": {
                "somestr": {
                    "type": "string",
                },
                "someint": {
                    "type": "integer",
                },
            },
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

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
    def test_object_with_properties_invalid(
        self, unmarshallers_factory, value
    ):
        schema = {
            "type": "object",
            "properties": {
                "somestr": {
                    "type": "string",
                },
                "someint": {
                    "type": "integer",
                },
            },
            "additionalProperties": False,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_default_property(self, unmarshallers_factory, value):
        schema = {
            "type": "object",
            "properties": {
                "prop": {
                    "type": "string",
                    "default": "value1",
                }
            },
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == {"prop": "value1"}

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
        ],
    )
    def test_object_additional_properties_false(
        self, unmarshallers_factory, value
    ):
        schema = {
            "type": "object",
            "additionalProperties": False,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
            {"foo": "bar", "bar": "foo"},
            {"additional": {"bar": 1}},
        ],
    )
    @pytest.mark.parametrize("additional_properties", [True, {}])
    def test_object_additional_properties_free_form_object(
        self, value, additional_properties, unmarshallers_factory
    ):
        schema = {
            "type": "object",
            "additionalProperties": additional_properties,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_object_additional_properties_list(self, unmarshallers_factory):
        schema = {"type": "object"}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal({"user_ids": [1, 2, 3, 4]})

        assert result == {
            "user_ids": [1, 2, 3, 4],
        }

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
        ],
    )
    def test_object_additional_properties(self, unmarshallers_factory, value):
        schema = {
            "type": "object",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
        ],
    )
    def test_object_additional_properties_object(
        self, unmarshallers_factory, value
    ):
        additional_properties = {
            "type": "integer",
        }
        schema = {
            "type": "object",
            "additionalProperties": additional_properties,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_min_properties(self, unmarshallers_factory, value):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "minProperties": 1,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_min_properties_invalid(self, unmarshallers_factory, value):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "minProperties": 4,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_min_properties_invalid_schema(
        self, unmarshallers_factory, value
    ):
        schema = {
            "type": "object",
            "minProperties": 2,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_max_properties(self, unmarshallers_factory, value):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "maxProperties": 3,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_max_properties_invalid(self, unmarshallers_factory, value):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "maxProperties": 0,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_max_properties_invalid_schema(
        self, unmarshallers_factory, value
    ):
        schema = {
            "type": "object",
            "maxProperties": -1,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    def test_any_one_of(self, unmarshallers_factory):
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = ["hello"]

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_any_any_of(self, unmarshallers_factory):
        schema = {
            "anyOf": [
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = ["hello"]

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_any_all_of(self, unmarshallers_factory):
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = ["hello"]

        result = unmarshaller.unmarshal(value)

        assert result == value

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
    def test_any_all_of_invalid_properties(self, value, unmarshallers_factory):
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    def test_any_format_one_of(self, unmarshallers_factory):
        schema = {
            "format": "date",
            "oneOf": [
                {"type": "integer"},
                {
                    "type": "string",
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = "2018-01-02"

        result = unmarshaller.unmarshal(value)

        assert result == date(2018, 1, 2)

    def test_any_one_of_any(self, unmarshallers_factory):
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
        unmarshaller = unmarshallers_factory.create(spec)
        value = "2018-01-02"

        result = unmarshaller.unmarshal(value)

        assert result == date(2018, 1, 2)

    def test_any_any_of_any(self, unmarshallers_factory):
        schema = {
            "anyOf": [
                {},
                {
                    "type": "string",
                    "format": "date",
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = "2018-01-02"

        result = unmarshaller.unmarshal(value)

        assert result == date(2018, 1, 2)

    def test_any_all_of_any(self, unmarshallers_factory):
        schema = {
            "allOf": [
                {},
                {
                    "type": "string",
                    "format": "date",
                },
            ],
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = "2018-01-02"

        result = unmarshaller.unmarshal(value)

        assert result == date(2018, 1, 2)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_any_of_no_valid(self, unmarshallers_factory, value):
        any_of = [
            {
                "type": "object",
                "required": ["test1"],
                "properties": {
                    "test1": {
                        "type": "string",
                    },
                },
            },
            {
                "type": "object",
                "required": ["test2"],
                "properties": {
                    "test2": {
                        "type": "string",
                    },
                },
            },
        ]
        schema = {
            "anyOf": any_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_any_one_of_no_valid(self, unmarshallers_factory, value):
        one_of = [
            {
                "type": "object",
                "required": [
                    "test1",
                ],
                "properties": {
                    "test1": {
                        "type": "string",
                    },
                },
            },
            {
                "type": "object",
                "required": [
                    "test2",
                ],
                "properties": {
                    "test2": {
                        "type": "string",
                    },
                },
            },
        ]
        schema = {
            "oneOf": one_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_any_any_of_different_type(self, unmarshallers_factory, value):
        any_of = [{"type": "integer"}, {"type": "string"}]
        schema = {
            "anyOf": any_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_any_one_of_different_type(self, unmarshallers_factory, value):
        one_of = [
            {
                "type": "integer",
            },
            {
                "type": "string",
            },
        ]
        schema = {
            "oneOf": one_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {
                "foo": "FOO",
            },
            {
                "foo": "FOO",
                "bar": "BAR",
            },
        ],
    )
    def test_any_any_of_unambiguous(self, unmarshallers_factory, value):
        any_of = [
            {
                "type": "object",
                "required": ["foo"],
                "properties": {
                    "foo": {
                        "type": "string",
                    },
                },
                "additionalProperties": False,
            },
            {
                "type": "object",
                "required": ["foo", "bar"],
                "properties": {
                    "foo": {
                        "type": "string",
                    },
                    "bar": {
                        "type": "string",
                    },
                },
                "additionalProperties": False,
            },
        ]
        schema = {
            "anyOf": any_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_multiple_any_of(self, unmarshallers_factory, value):
        any_of = [
            {
                "type": "object",
            },
            {
                "type": "object",
            },
        ]
        schema = {
            "type": "object",
            "anyOf": any_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            dict(),
        ],
    )
    def test_object_multiple_one_of(self, unmarshallers_factory, value):
        one_of = [
            {
                "type": "object",
            },
            {
                "type": "object",
            },
        ]
        schema = {
            "type": "object",
            "oneOf": one_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)

    @pytest.mark.parametrize(
        "value",
        [
            {
                "foo": "FOO",
            },
            {
                "foo": "FOO",
                "bar": "BAR",
            },
        ],
    )
    def test_any_one_of_unambiguous(self, unmarshallers_factory, value):
        one_of = [
            {
                "type": "object",
                "required": [
                    "foo",
                ],
                "properties": {
                    "foo": {
                        "type": "string",
                    },
                },
                "additionalProperties": False,
            },
            {
                "type": "object",
                "required": ["foo", "bar"],
                "properties": {
                    "foo": {
                        "type": "string",
                    },
                    "bar": {
                        "type": "string",
                    },
                },
                "additionalProperties": False,
            },
        ]
        schema = {
            "oneOf": one_of,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value


class BaseTestOASS30chemaUnmarshallersFactoryCall:
    def test_null_undefined(self, unmarshallers_factory):
        schema = {"type": "null"}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(UnknownType):
            unmarshaller.unmarshal(None)

    @pytest.mark.parametrize(
        "type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_nullable(self, unmarshallers_factory, type):
        schema = {"type": type, "nullable": True}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(None)

        assert result is None

    @pytest.mark.parametrize(
        "type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_not_nullable(self, unmarshallers_factory, type):
        schema = {"type": type}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(
            InvalidSchemaValue,
            match=f"not valid for schema of type {type}",
        ) as exc_info:
            unmarshaller.unmarshal(None)
        assert len(exc_info.value.schema_errors) == 2
        assert (
            "None for not nullable" in exc_info.value.schema_errors[0].message
        )
        assert (
            f"None is not of type '{type}'"
            in exc_info.value.schema_errors[1].message
        )

    @pytest.mark.parametrize(
        "type,format,value,unmarshalled",
        [
            ("string", "byte", "dGVzdA==", "test"),
            ("string", "binary", b"test", b"test"),
        ],
    )
    def test_basic_type_oas30_formats(
        self, unmarshallers_factory, type, format, value, unmarshalled
    ):
        schema = {
            "type": type,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == unmarshalled

    @pytest.mark.parametrize(
        "type,format,value",
        [
            ("string", "byte", "passwd"),
            ("string", "binary", "test"),
        ],
    )
    def test_basic_type_oas30_formats_invalid(
        self, unmarshallers_factory, type, format, value
    ):
        schema = {
            "type": type,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(
            InvalidSchemaValue,
            match=f"not valid for schema of type {type}",
        ) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            f"is not a '{format}'" in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.xfail(
        reason=(
            "OAS 3.0 string type checker allows byte. "
            "See https://github.com/python-openapi/openapi-schema-validator/issues/64"
        ),
        strict=True,
    )
    def test_string_format_binary_invalid(self, unmarshallers_factory):
        schema = {
            "type": "string",
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = b"true"

        with pytest.raises(
            InvalidSchemaValue,
            match=f"not valid for schema of type {type}",
        ):
            unmarshaller.unmarshal(value)

    @pytest.mark.xfail(
        reason=(
            "Rraises TypeError not SchemaError. "
            "See ttps://github.com/python-openapi/openapi-schema-validator/issues/65"
        ),
        strict=True,
    )
    @pytest.mark.parametrize(
        "types,value",
        [
            (["string", "null"], "string"),
            (["number", "null"], 2),
            (["number", "null"], 3.14),
            (["boolean", "null"], True),
            (["array", "null"], [1, 2]),
            (["object", "null"], {}),
        ],
    )
    def test_nultiple_types_undefined(
        self, unmarshallers_factory, types, value
    ):
        schema = {"type": types}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(SchemaError):
            unmarshaller.unmarshal(value)

    def test_integer_default_nullable(self, unmarshallers_factory):
        default_value = 123
        schema = {
            "type": "integer",
            "default": default_value,
            "nullable": True,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = None

        result = unmarshaller.unmarshal(value)

        assert result is None

    def test_array_nullable(self, unmarshallers_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "integer",
            },
            "nullable": True,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = None

        result = unmarshaller.unmarshal(value)

        assert result is None

    def test_object_property_nullable(self, unmarshallers_factory):
        schema = {
            "type": "object",
            "properties": {
                "foo": {
                    "type": "object",
                    "nullable": True,
                }
            },
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = {"foo": None}

        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_subschema_nullable(self, unmarshallers_factory):
        schema = {
            "oneOf": [
                {
                    "type": "integer",
                },
                {
                    "nullable": True,
                },
            ]
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = None

        result = unmarshaller.unmarshal(value)

        assert result is None


class TestOAS30RequestSchemaUnmarshallersFactory(
    BaseTestOASSchemaUnmarshallersFactoryCall,
    BaseTestOASS30chemaUnmarshallersFactoryCall,
):
    @pytest.fixture
    def unmarshallers_factory(self):
        return oas30_write_schema_unmarshallers_factory

    def test_write_only_properties(self, unmarshallers_factory):
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = {"id": 10}

        # readOnly properties may be admitted in a Response context
        result = unmarshaller.unmarshal(value)

        assert result == value

    def test_read_only_properties_invalid(self, unmarshallers_factory):
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = {"id": 10}

        # readOnly properties are not admitted on a Request context
        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal(value)


class TestOAS30ResponseSchemaUnmarshallersFactory(
    BaseTestOASSchemaUnmarshallersFactoryCall,
    BaseTestOASS30chemaUnmarshallersFactoryCall,
):
    @pytest.fixture
    def unmarshallers_factory(self):
        return oas30_read_schema_unmarshallers_factory

    def test_read_only_properties(self, unmarshallers_factory):
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        # readOnly properties may be admitted in a Response context
        result = unmarshaller.unmarshal({"id": 10})

        assert result == {
            "id": 10,
        }

    def test_write_only_properties_invalid(self, unmarshallers_factory):
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
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        # readOnly properties are not admitted on a Request context
        with pytest.raises(InvalidSchemaValue):
            unmarshaller.unmarshal({"id": 10})


class TestOAS31SchemaUnmarshallersFactory(
    BaseTestOASSchemaUnmarshallersFactoryCall
):
    @pytest.fixture
    def unmarshallers_factory(self):
        return oas31_schema_unmarshallers_factory

    @pytest.mark.xfail(
        reason=(
            "OpenAPI 3.1 schema validator uses OpenAPI 3.0 format checker."
            "See https://github.com/python-openapi/openapi-core/issues/506"
        ),
        strict=True,
    )
    @pytest.mark.parametrize(
        "type,format",
        [
            ("string", "byte"),
            ("string", "binary"),
        ],
    )
    def test_create_oas30_formatter_not_found(
        self, unmarshallers_factory, type, format
    ):
        schema = {
            "type": type,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)

        with pytest.raises(FormatterNotFoundError):
            unmarshallers_factory.create(spec)

    @pytest.mark.parametrize(
        "type,value",
        [
            ("string", b"test"),
            ("integer", b"test"),
            ("number", b"test"),
            ("array", b"test"),
            ("boolean", b"test"),
            ("object", b"test"),
        ],
    )
    def test_basic_types_invalid(self, unmarshallers_factory, type, value):
        schema = {
            "type": type,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(
            InvalidSchemaValue,
            match=f"not valid for schema of type {type}",
        ):
            unmarshaller.unmarshal(value)

    def test_null(self, unmarshallers_factory):
        schema = {"type": "null"}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(None)

        assert result is None

    @pytest.mark.parametrize("value", ["string", 2, 3.14, True, [1, 2], {}])
    def test_null_invalid(self, unmarshallers_factory, value):
        schema = {"type": "null"}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert (
            "is not of type 'null'" in exc_info.value.schema_errors[0].message
        )

    @pytest.mark.parametrize(
        "types,value",
        [
            (["string", "null"], "string"),
            (["number", "null"], 2),
            (["number", "null"], 3.14),
            (["boolean", "null"], True),
            (["array", "null"], [1, 2]),
            (["object", "null"], {}),
        ],
    )
    def test_nultiple_types(self, unmarshallers_factory, types, value):
        schema = {"type": types}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize(
        "types,value",
        [
            (["string", "null"], 2),
            (["number", "null"], "string"),
            (["number", "null"], True),
            (["boolean", "null"], 3.14),
            (["array", "null"], {}),
            (["object", "null"], [1, 2]),
        ],
    )
    def test_nultiple_types_invalid(self, unmarshallers_factory, types, value):
        schema = {"type": types}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        with pytest.raises(InvalidSchemaValue) as exc_info:
            unmarshaller.unmarshal(value)
        assert len(exc_info.value.schema_errors) == 1
        assert "is not of type" in exc_info.value.schema_errors[0].message

    @pytest.mark.parametrize(
        "types,format,value,expected",
        [
            (["string", "null"], "date", None, None),
            (["string", "null"], "date", "2018-12-13", date(2018, 12, 13)),
        ],
    )
    def test_multiple_types_format_valid_or_ignored(
        self, unmarshallers_factory, types, format, value, expected
    ):
        schema = {
            "type": types,
            "format": format,
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(value)

        assert result == expected

    def test_any_null(self, unmarshallers_factory):
        schema = {}
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)

        result = unmarshaller.unmarshal(None)

        assert result is None

    def test_subschema_null(self, unmarshallers_factory):
        schema = {
            "oneOf": [
                {
                    "type": "integer",
                },
                {
                    "type": "null",
                },
            ]
        }
        spec = SchemaPath.from_dict(schema)
        unmarshaller = unmarshallers_factory.create(spec)
        value = None

        result = unmarshaller.unmarshal(value)

        assert result is None
