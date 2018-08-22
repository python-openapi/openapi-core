import datetime

import mock
import pytest

from openapi_core.extensions.models.models import Model
from openapi_core.schema.schemas.exceptions import (
    InvalidSchemaValue, MultipleOneOfSchema, NoOneOfSchema, OpenAPISchemaError,
)
from openapi_core.schema.schemas.models import Schema

from six import b, u


class TestSchemaIteritems(object):

    @pytest.fixture
    def schema(self):
        properties = {
            'application/json': mock.sentinel.application_json,
            'text/csv': mock.sentinel.text_csv,
        }
        return Schema('object', properties=properties)

    @property
    def test_valid(self, schema):
        for name in schema.properties.keys():
            assert schema[name] == schema.properties[name]


class TestSchemaUnmarshal(object):

    def test_deprecated(self):
        schema = Schema('string', deprecated=True)
        value = 'test'

        with pytest.warns(DeprecationWarning):
            result = schema.unmarshal(value)

        assert result == value

    def test_string_valid(self):
        schema = Schema('string')
        value = 'test'

        result = schema.unmarshal(value)

        assert result == value

    def test_string_none(self):
        schema = Schema('string')
        value = None

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_string_default(self):
        default_value = 'default'
        schema = Schema('string', default=default_value)
        value = None

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_string_default_nullable(self):
        default_value = 'default'
        schema = Schema('string', default=default_value, nullable=True)
        value = None

        result = schema.unmarshal(value)

        assert result == default_value

    def test_string_format_date(self):
        schema = Schema('string', schema_format='date')
        value = '2018-01-02'

        result = schema.unmarshal(value)

        assert result == datetime.date(2018, 1, 2)

    def test_string_format_datetime(self):
        schema = Schema('string', schema_format='date-time')
        value = '2018-01-02T00:00:00'

        result = schema.unmarshal(value)

        assert result == datetime.datetime(2018, 1, 2, 0, 0, 0)

    @pytest.mark.xfail(reason="No custom formats support atm")
    def test_string_format_custom(self):
        custom_format = 'custom'
        schema = Schema('string', schema_format=custom_format)
        value = 'x'

        with mock.patch.dict(
            Schema.STRING_FORMAT_CAST_CALLABLE_GETTER,
            {custom_format: lambda x: x + '-custom'},
        ):
            result = schema.unmarshal(value)

        assert result == 'x-custom'

    def test_string_format_unknown(self):
        unknown_format = 'unknown'
        schema = Schema('string', schema_format=unknown_format)
        value = 'x'

        with pytest.raises(OpenAPISchemaError):
            schema.unmarshal(value)

    @pytest.mark.xfail(reason="No custom formats support atm")
    def test_string_format_invalid_value(self):
        custom_format = 'custom'
        schema = Schema('string', schema_format=custom_format)
        value = 'x'

        with mock.patch.dict(
            Schema.STRING_FORMAT_CAST_CALLABLE_GETTER,
            {custom_format: mock.Mock(side_effect=ValueError())},
        ), pytest.raises(
            InvalidSchemaValue, message='Failed to format value'
        ):
            schema.unmarshal(value)

    def test_integer_valid(self):
        schema = Schema('integer')
        value = '123'

        result = schema.unmarshal(value)

        assert result == int(value)

    def test_integer_enum_invalid(self):
        schema = Schema('integer', enum=[1, 2, 3])
        value = '123'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_integer_enum(self):
        schema = Schema('integer', enum=[1, 2, 3])
        value = '2'

        result = schema.unmarshal(value)

        assert result == int(value)

    def test_integer_default(self):
        default_value = '123'
        schema = Schema('integer', default=default_value)
        value = None

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_integer_default_nullable(self):
        default_value = '123'
        schema = Schema('integer', default=default_value, nullable=True)
        value = None

        result = schema.unmarshal(value)

        assert result == default_value

    def test_integer_invalid(self):
        schema = Schema('integer')
        value = 'abc'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)


class TestSchemaValidate(object):

    @pytest.mark.parametrize('schema_type', [
        'boolean', 'array', 'integer', 'number', 'string',
    ])
    def test_null(self, schema_type):
        schema = Schema(schema_type)
        value = None

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('schema_type', [
        'boolean', 'array', 'integer', 'number', 'string',
    ])
    def test_nullable(self, schema_type):
        schema = Schema(schema_type, nullable=True)
        value = None

        result = schema.validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [False, True])
    def test_boolean(self, value):
        schema = Schema('boolean')

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [1, 3.14, u('true'), [True, False]])
    def test_boolean_invalid(self, value):
        schema = Schema('boolean')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [[1, 2], (3, 4)])
    def test_array_no_schema(self, value):
        schema = Schema('array')

        with pytest.raises(OpenAPISchemaError):
            schema.validate(value)

    @pytest.mark.parametrize('value', [[1, 2], (3, 4)])
    def test_array(self, value):
        schema = Schema('array', items=Schema('integer'))

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [False, 1, 3.14, u('true')])
    def test_array_invalid(self, value):
        schema = Schema('array')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [1, 3])
    def test_integer(self, value):
        schema = Schema('integer')

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [False, 3.14, u('true'), [1, 2]])
    def test_integer_invalid(self, value):
        schema = Schema('integer')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [1, 3.14])
    def test_number(self, value):
        schema = Schema('number')

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [False, 'true', [1, 3]])
    def test_number_invalid(self, value):
        schema = Schema('number')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [u('true'), ])
    def test_string(self, value):
        schema = Schema('string')

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [b('test'), False, 1, 3.14, [1, 3]])
    def test_string_invalid(self, value):
        schema = Schema('string')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [
        b('true'), u('test'), False, 1, 3.14, [1, 3],
        datetime.datetime(1989, 1, 2),
    ])
    def test_string_format_date_invalid(self, value):
        schema = Schema('string', schema_format='date')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [
        datetime.date(1989, 1, 2), datetime.date(2018, 1, 2),
    ])
    def test_string_format_date(self, value):
        schema = Schema('string', schema_format='date')

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [
        b('true'), u('true'), False, 1, 3.14, [1, 3],
        datetime.date(1989, 1, 2),
    ])
    def test_string_format_datetime_invalid(self, value):
        schema = Schema('string', schema_format='date-time')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [
        datetime.datetime(1989, 1, 2, 0, 0, 0),
        datetime.datetime(2018, 1, 2, 23, 59, 59),
    ])
    def test_string_format_datetime(self, value):
        schema = Schema('string', schema_format='date-time')

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [
        u('true'), False, 1, 3.14, [1, 3], datetime.date(1989, 1, 2),
        datetime.datetime(1989, 1, 2, 0, 0, 0),
    ])
    def test_string_format_binary_invalid(self, value):
        schema = Schema('string', schema_format='binary')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [
        b('stream'), b('text'),
    ])
    def test_string_format_binary(self, value):
        schema = Schema('string', schema_format='binary')

        result = schema.validate(value)

        assert result == value

    @pytest.mark.parametrize('value', [
        u('test'), b('stream'), datetime.date(1989, 1, 2),
        datetime.datetime(1989, 1, 2, 0, 0, 0),
    ])
    def test_string_format_unknown(self, value):
        unknown_format = 'unknown'
        schema = Schema('string', schema_format=unknown_format)

        with pytest.raises(OpenAPISchemaError):
            schema.validate(value)

    @pytest.mark.parametrize('value', ['true', False, 1, 3.14, [1, 3]])
    def test_object_not_an_object(self, value):
        schema = Schema('object')

        with pytest.raises(InvalidSchemaValue):
            schema.validate(value)

    @pytest.mark.parametrize('value', [Model(), ])
    def test_object_multiple_one_of(self, value):
        one_of = [
            Schema('object'), Schema('object'),
        ]
        schema = Schema('object', one_of=one_of)

        with pytest.raises(MultipleOneOfSchema):
            schema.validate(value)

    @pytest.mark.parametrize('value', [Model(), ])
    def test_object_defferent_type_one_of(self, value):
        one_of = [
            Schema('integer'), Schema('string'),
        ]
        schema = Schema('object', one_of=one_of)

        with pytest.raises(MultipleOneOfSchema):
            schema.validate(value)

    @pytest.mark.parametrize('value', [Model(), ])
    def test_object_no_one_of(self, value):
        one_of = [
            Schema(
                'object',
                properties={'test1': Schema('string')},
                required=['test1', ],
            ),
            Schema(
                'object',
                properties={'test2': Schema('string')},
                required=['test2', ],
            ),
        ]
        schema = Schema('object', one_of=one_of)

        with pytest.raises(NoOneOfSchema):
            schema.validate(value)

    @pytest.mark.parametrize('value', [Model(), ])
    def test_object_default_property(self, value):
        schema = Schema('object', default='value1')

        result = schema.validate(value)

        assert result == value
