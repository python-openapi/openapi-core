import datetime

import mock
import pytest

from openapi_core.extensions.models.models import Model
from openapi_core.schema.schemas.exceptions import OpenAPISchemaError
from openapi_core.schema.schemas.models import Schema
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError, InvalidSchemaValue,
)
from openapi_core.unmarshalling.schemas.util import build_format_checker

from six import b, u


class TestSchemaValidate(object):

    @pytest.fixture
    def validator_factory(self):
        def create_validator(schema):
            format_checker = build_format_checker()
            return SchemaUnmarshallersFactory(
                format_checker=format_checker).create(schema)
        return create_validator

    @pytest.mark.parametrize('schema_type', [
        'boolean', 'array', 'integer', 'number', 'string',
    ])
    def test_null(self, schema_type, validator_factory):
        schema = Schema(schema_type)
        value = None

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('schema_type', [
        'boolean', 'array', 'integer', 'number', 'string',
    ])
    def test_nullable(self, schema_type, validator_factory):
        schema = Schema(schema_type, nullable=True)
        value = None

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.xfail(
        reason="validation does not care about custom formats atm")
    def test_string_format_custom_missing(self, validator_factory):
        custom_format = 'custom'
        schema = Schema('string', schema_format=custom_format)
        value = 'x'

        with pytest.raises(OpenAPISchemaError):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [False, True])
    def test_boolean(self, value, validator_factory):
        schema = Schema('boolean')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [1, 3.14, u('true'), [True, False]])
    def test_boolean_invalid(self, value, validator_factory):
        schema = Schema('boolean')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [(1, 2)])
    def test_array_no_schema(self, value, validator_factory):
        schema = Schema('array')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [[1, 2]])
    def test_array(self, value, validator_factory):
        schema = Schema('array', items=Schema('integer'))

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [False, 1, 3.14, u('true'), (3, 4)])
    def test_array_invalid(self, value, validator_factory):
        schema = Schema('array')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [1, 3])
    def test_integer(self, value, validator_factory):
        schema = Schema('integer')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [False, 3.14, u('true'), [1, 2]])
    def test_integer_invalid(self, value, validator_factory):
        schema = Schema('integer')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [0, 1, 2])
    def test_integer_minimum_invalid(self, value, validator_factory):
        schema = Schema('integer', minimum=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [4, 5, 6])
    def test_integer_minimum(self, value, validator_factory):
        schema = Schema('integer', minimum=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [4, 5, 6])
    def test_integer_maximum_invalid(self, value, validator_factory):
        schema = Schema('integer', maximum=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [0, 1, 2])
    def test_integer_maximum(self, value, validator_factory):
        schema = Schema('integer', maximum=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [1, 2, 4])
    def test_integer_multiple_of_invalid(self, value, validator_factory):
        schema = Schema('integer', multiple_of=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [3, 6, 18])
    def test_integer_multiple_of(self, value, validator_factory):
        schema = Schema('integer', multiple_of=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [1, 3.14])
    def test_number(self, value, validator_factory):
        schema = Schema('number')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [False, 'true', [1, 3]])
    def test_number_invalid(self, value, validator_factory):
        schema = Schema('number')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [0, 1, 2])
    def test_number_minimum_invalid(self, value, validator_factory):
        schema = Schema('number', minimum=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [3, 4, 5])
    def test_number_minimum(self, value, validator_factory):
        schema = Schema('number', minimum=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [1, 2, 3])
    def test_number_exclusive_minimum_invalid(self, value, validator_factory):
        schema = Schema('number', minimum=3, exclusive_minimum=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [4, 5, 6])
    def test_number_exclusive_minimum(self, value, validator_factory):
        schema = Schema('number', minimum=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [4, 5, 6])
    def test_number_maximum_invalid(self, value, validator_factory):
        schema = Schema('number', maximum=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [1, 2, 3])
    def test_number_maximum(self, value, validator_factory):
        schema = Schema('number', maximum=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [3, 4, 5])
    def test_number_exclusive_maximum_invalid(self, value, validator_factory):
        schema = Schema('number', maximum=3, exclusive_maximum=True)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [0, 1, 2])
    def test_number_exclusive_maximum(self, value, validator_factory):
        schema = Schema('number', maximum=3, exclusive_maximum=True)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [1, 2, 4])
    def test_number_multiple_of_invalid(self, value, validator_factory):
        schema = Schema('number', multiple_of=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [3, 6, 18])
    def test_number_multiple_of(self, value, validator_factory):
        schema = Schema('number', multiple_of=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [u('true'), b('test')])
    def test_string(self, value, validator_factory):
        schema = Schema('string')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [False, 1, 3.14, [1, 3]])
    def test_string_invalid(self, value, validator_factory):
        schema = Schema('string')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        b('true'), u('test'), False, 1, 3.14, [1, 3],
        datetime.datetime(1989, 1, 2),
    ])
    def test_string_format_date_invalid(self, value, validator_factory):
        schema = Schema('string', schema_format='date')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        u('1989-01-02'), u('2018-01-02'),
    ])
    def test_string_format_date(self, value, validator_factory):
        schema = Schema('string', schema_format='date')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [
        u('12345678-1234-5678-1234-567812345678'),
    ])
    def test_string_format_uuid(self, value, validator_factory):
        schema = Schema('string', schema_format='uuid')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [
        b('true'), u('true'), False, 1, 3.14, [1, 3],
        datetime.date(2018, 1, 2), datetime.datetime(2018, 1, 2, 23, 59, 59),
    ])
    def test_string_format_uuid_invalid(self, value, validator_factory):
        schema = Schema('string', schema_format='uuid')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        b('true'), u('true'), False, 1, 3.14, [1, 3],
        u('1989-01-02'),
    ])
    def test_string_format_datetime_invalid(self, value, validator_factory):
        schema = Schema('string', schema_format='date-time')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        u('1989-01-02T00:00:00Z'),
        u('2018-01-02T23:59:59Z'),
    ])
    @mock.patch(
        'openapi_schema_validator._format.'
        'DATETIME_HAS_STRICT_RFC3339', True
    )
    @mock.patch(
        'openapi_schema_validator._format.'
        'DATETIME_HAS_ISODATE', False
    )
    def test_string_format_datetime_strict_rfc3339(
            self, value, validator_factory):
        schema = Schema('string', schema_format='date-time')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [
        u('1989-01-02T00:00:00Z'),
        u('2018-01-02T23:59:59Z'),
    ])
    @mock.patch(
        'openapi_schema_validator._format.'
        'DATETIME_HAS_STRICT_RFC3339', False
    )
    @mock.patch(
        'openapi_schema_validator._format.'
        'DATETIME_HAS_ISODATE', True
    )
    def test_string_format_datetime_isodate(self, value, validator_factory):
        schema = Schema('string', schema_format='date-time')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [
        u('true'), False, 1, 3.14, [1, 3], u('1989-01-02'),
        u('1989-01-02T00:00:00Z'),
    ])
    def test_string_format_binary_invalid(self, value, validator_factory):
        schema = Schema('string', schema_format='binary')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        b('stream'), b('text'),
    ])
    def test_string_format_binary(self, value, validator_factory):
        schema = Schema('string', schema_format='binary')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [
        b('dGVzdA=='), u('dGVzdA=='),
    ])
    def test_string_format_byte(self, value, validator_factory):
        schema = Schema('string', schema_format='byte')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [
        u('tsssst'), b('tsssst'), b('tesddddsdsdst'),
    ])
    def test_string_format_byte_invalid(self, value, validator_factory):
        schema = Schema('string', schema_format='byte')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        u('test'), b('stream'), datetime.date(1989, 1, 2),
        datetime.datetime(1989, 1, 2, 0, 0, 0),
    ])
    def test_string_format_unknown(self, value, validator_factory):
        unknown_format = 'unknown'
        schema = Schema('string', schema_format=unknown_format)

        with pytest.raises(FormatterNotFoundError):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [u(""), u("a"), u("ab")])
    def test_string_min_length_invalid(self, value, validator_factory):
        schema = Schema('string', min_length=3)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [u("abc"), u("abcd")])
    def test_string_min_length(self, value, validator_factory):
        schema = Schema('string', min_length=3)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [u(""), ])
    def test_string_max_length_invalid_schema(self, value, validator_factory):
        schema = Schema('string', max_length=-1)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [u("ab"), u("abc")])
    def test_string_max_length_invalid(self, value, validator_factory):
        schema = Schema('string', max_length=1)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [u(""), u("a")])
    def test_string_max_length(self, value, validator_factory):
        schema = Schema('string', max_length=1)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [u("foo"), u("bar")])
    def test_string_pattern_invalid(self, value, validator_factory):
        schema = Schema('string', pattern='baz')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [u("bar"), u("foobar")])
    def test_string_pattern(self, value, validator_factory):
        schema = Schema('string', pattern='bar')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', ['true', False, 1, 3.14, [1, 3]])
    def test_object_not_an_object(self, value, validator_factory):
        schema = Schema('object')

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [Model(), ])
    def test_object_multiple_one_of(self, value, validator_factory):
        one_of = [
            Schema('object'), Schema('object'),
        ]
        schema = Schema('object', one_of=one_of)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [{}, ])
    def test_object_different_type_one_of(self, value, validator_factory):
        one_of = [
            Schema('integer'), Schema('string'),
        ]
        schema = Schema('object', one_of=one_of)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [{}, ])
    def test_object_no_one_of(self, value, validator_factory):
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

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        {
            'foo': u("FOO"),
        },
        {
            'foo': u("FOO"),
            'bar': u("BAR"),
        },
    ])
    def test_unambiguous_one_of(self, value, validator_factory):
        one_of = [
            Schema(
                'object',
                properties={
                    'foo': Schema('string'),
                },
                additional_properties=False,
                required=['foo'],
            ),
            Schema(
                'object',
                properties={
                    'foo': Schema('string'),
                    'bar': Schema('string'),
                },
                additional_properties=False,
                required=['foo', 'bar'],
            ),
        ]
        schema = Schema('object', one_of=one_of)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [{}, ])
    def test_object_default_property(self, value, validator_factory):
        schema = Schema('object', default='value1')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [{}, ])
    def test_object_min_properties_invalid_schema(
            self, value, validator_factory):
        schema = Schema('object', min_properties=2)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        {'a': 1},
        {'a': 1, 'b': 2},
        {'a': 1, 'b': 2, 'c': 3},
    ])
    def test_object_min_properties_invalid(self, value, validator_factory):
        schema = Schema(
            'object',
            properties={k: Schema('number')
                        for k in ['a', 'b', 'c']},
            min_properties=4,
        )

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        {'a': 1},
        {'a': 1, 'b': 2},
        {'a': 1, 'b': 2, 'c': 3},
    ])
    def test_object_min_properties(self, value, validator_factory):
        schema = Schema(
            'object',
            properties={k: Schema('number')
                        for k in ['a', 'b', 'c']},
            min_properties=1,
        )

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [{}, ])
    def test_object_max_properties_invalid_schema(
            self, value, validator_factory):
        schema = Schema('object', max_properties=-1)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        {'a': 1},
        {'a': 1, 'b': 2},
        {'a': 1, 'b': 2, 'c': 3},
    ])
    def test_object_max_properties_invalid(self, value, validator_factory):
        schema = Schema(
            'object',
            properties={k: Schema('number')
                        for k in ['a', 'b', 'c']},
            max_properties=0,
        )

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        {'a': 1},
        {'a': 1, 'b': 2},
        {'a': 1, 'b': 2, 'c': 3},
    ])
    def test_object_max_properties(self, value, validator_factory):
        schema = Schema(
            'object',
            properties={k: Schema('number')
                        for k in ['a', 'b', 'c']},
            max_properties=3,
        )

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [{'additional': 1}, ])
    def test_object_additional_properties(self, value, validator_factory):
        schema = Schema('object')

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [{'additional': 1}, ])
    def test_object_additional_properties_false(
            self, value, validator_factory):
        schema = Schema('object', additional_properties=False)

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [{'additional': 1}, ])
    def test_object_additional_properties_object(
            self, value, validator_factory):
        additional_properties = Schema('integer')
        schema = Schema('object', additional_properties=additional_properties)

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [[], [1], [1, 2]])
    def test_list_min_items_invalid(self, value, validator_factory):
        schema = Schema(
            'array',
            items=Schema('number'),
            min_items=3,
        )

        with pytest.raises(Exception):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [[], [1], [1, 2]])
    def test_list_min_items(self, value, validator_factory):
        schema = Schema(
            'array',
            items=Schema('number'),
            min_items=0,
        )

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [[], ])
    def test_list_max_items_invalid_schema(self, value, validator_factory):
        schema = Schema(
            'array',
            items=Schema('number'),
            max_items=-1,
        )

        with pytest.raises(InvalidSchemaValue):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [[1, 2], [2, 3, 4]])
    def test_list_max_items_invalid(self, value, validator_factory):
        schema = Schema(
            'array',
            items=Schema('number'),
            max_items=1,
        )

        with pytest.raises(Exception):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [[1, 2, 1], [2, 2]])
    def test_list_unique_items_invalid(self, value, validator_factory):
        schema = Schema(
            'array',
            items=Schema('number'),
            unique_items=True,
        )

        with pytest.raises(Exception):
            validator_factory(schema).validate(value)

    @pytest.mark.parametrize('value', [
        {
            'someint': 123,
        },
        {
            'somestr': u('content'),
        },
        {
            'somestr': u('content'),
            'someint': 123,
        },
    ])
    def test_object_with_properties(self, value, validator_factory):
        schema = Schema(
            'object',
            properties={
                'somestr': Schema('string'),
                'someint': Schema('integer'),
            },
        )

        result = validator_factory(schema).validate(value)

        assert result is None

    @pytest.mark.parametrize('value', [
        {
            'somestr': {},
            'someint': 123,
        },
        {
            'somestr': [
                'content1', 'content2'
            ],
            'someint': 123,
        },
        {
            'somestr': 123,
            'someint': 123,
        },
        {
            'somestr': 'content',
            'someint': 123,
            'not_in_scheme_prop': 123,
        },
    ])
    def test_object_with_invalid_properties(self, value, validator_factory):
        schema = Schema(
            'object',
            properties={
                'somestr': Schema('string'),
                'someint': Schema('integer'),
            },
            additional_properties=False,
        )

        with pytest.raises(Exception):
            validator_factory(schema).validate(value)
