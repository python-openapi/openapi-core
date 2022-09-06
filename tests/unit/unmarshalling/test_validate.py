import datetime
from unittest import mock

import pytest

from openapi_core.extensions.models.models import Model
from openapi_core.spec.paths import Spec
from openapi_core.unmarshalling.schemas import (
    oas30_request_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue


class TestSchemaValidate:
    @pytest.fixture
    def validator_factory(self):
        def create_validator(schema):
            return oas30_request_schema_unmarshallers_factory.create(schema)

        return create_validator

    @pytest.mark.parametrize(
        "schema_type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_null(self, schema_type, validator_factory):
        schema = {
            "type": schema_type,
        }
        spec = Spec.from_dict(schema)
        value = None

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "schema_type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_nullable(self, schema_type, validator_factory):
        schema = {
            "type": schema_type,
            "nullable": True,
        }
        spec = Spec.from_dict(schema)
        value = None

        result = validator_factory(spec).validate(value)

        assert result is None

    def test_string_format_custom_missing(self, validator_factory):
        custom_format = "custom"
        schema = {
            "type": "string",
            "format": custom_format,
        }
        spec = Spec.from_dict(schema)
        value = "x"

        with pytest.raises(FormatterNotFoundError):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [False, True])
    def test_boolean(self, value, validator_factory):
        schema = {
            "type": "boolean",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 3.14, "true", [True, False]])
    def test_boolean_invalid(self, value, validator_factory):
        schema = {
            "type": "boolean",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [(1, 2)])
    def test_array_no_schema(self, value, validator_factory):
        schema = {
            "type": "array",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [[1, 2]])
    def test_array(self, value, validator_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "integer",
            },
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [False, 1, 3.14, "true", (3, 4)])
    def test_array_invalid(self, value, validator_factory):
        schema = {
            "type": "array",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [1, 3])
    def test_integer(self, value, validator_factory):
        schema = {
            "type": "integer",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [False, 3.14, "true", [1, 2]])
    def test_integer_invalid(self, value, validator_factory):
        schema = {
            "type": "integer",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_integer_minimum_invalid(self, value, validator_factory):
        schema = {
            "type": "integer",
            "minimum": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_integer_minimum(self, value, validator_factory):
        schema = {
            "type": "integer",
            "minimum": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_integer_maximum_invalid(self, value, validator_factory):
        schema = {
            "type": "integer",
            "maximum": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_integer_maximum(self, value, validator_factory):
        schema = {
            "type": "integer",
            "maximum": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 2, 4])
    def test_integer_multiple_of_invalid(self, value, validator_factory):
        schema = {
            "type": "integer",
            "multipleOf": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [3, 6, 18])
    def test_integer_multiple_of(self, value, validator_factory):
        schema = {
            "type": "integer",
            "multipleOf": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 3.14])
    def test_number(self, value, validator_factory):
        schema = {
            "type": "number",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [False, "true", [1, 3]])
    def test_number_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_number_minimum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [3, 4, 5])
    def test_number_minimum(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_number_exclusive_minimum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
            "exclusiveMinimum": True,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_number_exclusive_minimum(self, value, validator_factory):
        schema = {
            "type": "number",
            "minimum": 3,
            "exclusiveMinimum": True,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [4, 5, 6])
    def test_number_maximum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_number_maximum(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [3, 4, 5])
    def test_number_exclusive_maximum_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
            "exclusiveMaximum": True,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [0, 1, 2])
    def test_number_exclusive_maximum(self, value, validator_factory):
        schema = {
            "type": "number",
            "maximum": 3,
            "exclusiveMaximum": True,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [1, 2, 4])
    def test_number_multiple_of_invalid(self, value, validator_factory):
        schema = {
            "type": "number",
            "multipleOf": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [3, 6, 18])
    def test_number_multiple_of(self, value, validator_factory):
        schema = {
            "type": "number",
            "multipleOf": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", ["true", b"test"])
    def test_string(self, value, validator_factory):
        schema = {
            "type": "string",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [False, 1, 3.14, [1, 3]])
    def test_string_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            b"true",
            "test",
            False,
            1,
            3.14,
            [1, 3],
            datetime.datetime(1989, 1, 2),
        ],
    )
    def test_string_format_date_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "date",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02",
            "2018-01-02",
        ],
    )
    def test_string_format_date(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "date",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "12345678-1234-5678-1234-567812345678",
        ],
    )
    def test_string_format_uuid(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "uuid",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            b"true",
            "true",
            False,
            1,
            3.14,
            [1, 3],
            datetime.date(2018, 1, 2),
            datetime.datetime(2018, 1, 2, 23, 59, 59),
        ],
    )
    def test_string_format_uuid_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "uuid",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            b"true",
            "true",
            False,
            1,
            3.14,
            [1, 3],
            "1989-01-02",
        ],
    )
    def test_string_format_datetime_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339", True
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", False
    )
    def test_string_format_datetime_strict_rfc3339(
        self, value, validator_factory
    ):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", True
    )
    def test_string_format_datetime_isodate(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "date-time",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "true",
            False,
            1,
            3.14,
            [1, 3],
            "1989-01-02",
            "1989-01-02T00:00:00Z",
        ],
    )
    def test_string_format_binary_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "binary",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            b"stream",
            b"text",
        ],
    )
    def test_string_format_binary(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "binary",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            b"dGVzdA==",
            "dGVzdA==",
        ],
    )
    def test_string_format_byte(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "byte",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "tsssst",
            b"tsssst",
            b"tesddddsdsdst",
        ],
    )
    def test_string_format_byte_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "format": "byte",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            "test",
            b"stream",
            datetime.date(1989, 1, 2),
            datetime.datetime(1989, 1, 2, 0, 0, 0),
        ],
    )
    def test_string_format_unknown(self, value, validator_factory):
        unknown_format = "unknown"
        schema = {
            "type": "string",
            "format": unknown_format,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(FormatterNotFoundError):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", ["", "a", "ab"])
    def test_string_min_length_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "minLength": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", ["abc", "abcd"])
    def test_string_min_length(self, value, validator_factory):
        schema = {
            "type": "string",
            "minLength": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "",
        ],
    )
    def test_string_max_length_invalid_schema(self, value, validator_factory):
        schema = {
            "type": "string",
            "maxLength": -1,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", ["ab", "abc"])
    def test_string_max_length_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "maxLength": 1,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", ["", "a"])
    def test_string_max_length(self, value, validator_factory):
        schema = {
            "type": "string",
            "maxLength": 1,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", ["foo", "bar"])
    def test_string_pattern_invalid(self, value, validator_factory):
        schema = {
            "type": "string",
            "pattern": "baz",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", ["bar", "foobar"])
    def test_string_pattern(self, value, validator_factory):
        schema = {
            "type": "string",
            "pattern": "bar",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", ["true", False, 1, 3.14, [1, 3]])
    def test_object_not_an_object(self, value, validator_factory):
        schema = {
            "type": "object",
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            Model(),
        ],
    )
    def test_object_multiple_one_of(self, value, validator_factory):
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
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_different_type_one_of(self, value, validator_factory):
        one_of = [
            {
                "type": "integer",
            },
            {
                "type": "string",
            },
        ]
        schema = {
            "type": "object",
            "oneOf": one_of,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_no_one_of(self, value, validator_factory):
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
            "type": "object",
            "oneOf": one_of,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

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
    def test_unambiguous_one_of(self, value, validator_factory):
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
            "type": "object",
            "oneOf": one_of,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_default_property(self, value, validator_factory):
        schema = {
            "type": "object",
            "default": "value1",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_min_properties_invalid_schema(
        self, value, validator_factory
    ):
        schema = {
            "type": "object",
            "minProperties": 2,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_min_properties_invalid(self, value, validator_factory):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "minProperties": 4,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_min_properties(self, value, validator_factory):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "minProperties": 1,
        }
        spec = Spec.from_dict(schema)
        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            {},
        ],
    )
    def test_object_max_properties_invalid_schema(
        self, value, validator_factory
    ):
        schema = {
            "type": "object",
            "maxProperties": -1,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_max_properties_invalid(self, value, validator_factory):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "maxProperties": 0,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    def test_object_max_properties(self, value, validator_factory):
        schema = {
            "type": "object",
            "properties": {k: {"type": "number"} for k in ["a", "b", "c"]},
            "maxProperties": 3,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
        ],
    )
    def test_object_additional_properties(self, value, validator_factory):
        schema = {
            "type": "object",
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
        ],
    )
    def test_object_additional_properties_false(
        self, value, validator_factory
    ):
        schema = {
            "type": "object",
            "additionalProperties": False,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            {"additional": 1},
        ],
    )
    def test_object_additional_properties_object(
        self, value, validator_factory
    ):
        additional_properties = {
            "type": "integer",
        }
        schema = {
            "type": "object",
            "additionalProperties": additional_properties,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize("value", [[], [1], [1, 2]])
    def test_list_min_items_invalid(self, value, validator_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "minItems": 3,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(Exception):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [[], [1], [1, 2]])
    def test_list_min_items(self, value, validator_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "minItems": 0,
        }
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            [],
        ],
    )
    def test_list_max_items_invalid_schema(self, value, validator_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "maxItems": -1,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [[1, 2], [2, 3, 4]])
    def test_list_max_items_invalid(self, value, validator_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "maxItems": 1,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(Exception):
            validator_factory(spec).validate(value)

    @pytest.mark.parametrize("value", [[1, 2, 1], [2, 2]])
    def test_list_unique_items_invalid(self, value, validator_factory):
        schema = {
            "type": "array",
            "items": {
                "type": "number",
            },
            "uniqueItems": True,
        }
        spec = Spec.from_dict(schema)

        with pytest.raises(Exception):
            validator_factory(spec).validate(value)

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
    def test_object_with_properties(self, value, validator_factory):
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
        spec = Spec.from_dict(schema)

        result = validator_factory(spec).validate(value)

        assert result is None

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
    def test_object_with_invalid_properties(self, value, validator_factory):
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
        spec = Spec.from_dict(schema)

        with pytest.raises(Exception):
            validator_factory(spec).validate(value)
