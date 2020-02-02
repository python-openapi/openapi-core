import datetime
import uuid

import mock
import pytest

from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.schemas.models import Schema
from openapi_core.schema.schemas.types import NoValue
from openapi_core.unmarshalling.schemas.exceptions import (
    InvalidSchemaFormatValue,
    FormatterNotFoundError,
    UnmarshalError,
    InvalidSchemaValue,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter


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
        for name in schema.properties:
            assert schema[name] == schema.properties[name]


class TestSchemaUnmarshal(object):

    def test_deprecated(self):
        schema = Schema('string', deprecated=True)
        value = 'test'

        with pytest.warns(DeprecationWarning):
            result = schema.unmarshal(value)

        assert result == value

    @pytest.mark.parametrize('schema_type', [
        'boolean', 'array', 'integer', 'number',
    ])
    def test_non_string_empty_value(self, schema_type):
        schema = Schema(schema_type)
        value = ''

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_string_valid(self):
        schema = Schema('string')
        value = 'test'

        result = schema.unmarshal(value)

        assert result == value

    def test_string_format_uuid_valid(self):
        schema = Schema(SchemaType.STRING, schema_format='uuid')
        value = str(uuid.uuid4())

        result = schema.unmarshal(value)

        assert result == uuid.UUID(value)

    def test_string_format_uuid_uuid_quirks_invalid(self):
        schema = Schema(SchemaType.STRING, schema_format='uuid')
        value = uuid.uuid4()

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_string_format_password(self):
        schema = Schema(SchemaType.STRING, schema_format='password')
        value = 'password'

        result = schema.unmarshal(value)

        assert result == 'password'

    def test_string_float_invalid(self):
        schema = Schema('string')
        value = 1.23

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_string_default(self):
        default_value = 'default'
        schema = Schema('string', default=default_value)
        value = NoValue

        result = schema.unmarshal(value)

        assert result == default_value

    @pytest.mark.parametrize('default_value', ['default', None])
    def test_string_default_nullable(self, default_value):
        schema = Schema('string', default=default_value, nullable=True)
        value = NoValue

        result = schema.unmarshal(value)

        assert result == default_value

    def test_string_format_date(self):
        schema = Schema('string', schema_format='date')
        value = '2018-01-02'

        result = schema.unmarshal(value)

        assert result == datetime.date(2018, 1, 2)

    def test_string_format_datetime(self):
        schema = Schema('string', schema_format='date-time')
        value = '2018-01-02T00:00:00Z'

        result = schema.unmarshal(value)

        assert result == datetime.datetime(2018, 1, 2, 0, 0)

    def test_string_format_custom(self):
        formatted = 'x-custom'

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                return formatted
        custom_format = 'custom'
        schema = Schema('string', schema_format=custom_format)
        value = 'x'
        formatter = CustomFormatter()
        custom_formatters = {
            custom_format: formatter,
        }

        result = schema.unmarshal(value, custom_formatters=custom_formatters)

        assert result == formatted

    def test_string_format_custom_value_error(self):

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                raise ValueError
        custom_format = 'custom'
        schema = Schema('string', schema_format=custom_format)
        value = 'x'
        formatter = CustomFormatter()
        custom_formatters = {
            custom_format: formatter,
        }

        with pytest.raises(InvalidSchemaFormatValue):
            schema.unmarshal(
                value, custom_formatters=custom_formatters)

    def test_string_format_unknown(self):
        unknown_format = 'unknown'
        schema = Schema('string', schema_format=unknown_format)
        value = 'x'

        with pytest.raises(FormatterNotFoundError):
            schema.unmarshal(value)

    def test_string_format_invalid_value(self):
        custom_format = 'custom'
        schema = Schema('string', schema_format=custom_format)
        value = 'x'

        with pytest.raises(
            FormatterNotFoundError,
            message=(
                'Formatter not found for custom format'
            ),
        ):
            schema.unmarshal(value)

    def test_integer_valid(self):
        schema = Schema('integer')
        value = 123

        result = schema.unmarshal(value)

        assert result == int(value)

    def test_integer_string_invalid(self):
        schema = Schema('integer')
        value = '123'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_integer_enum_invalid(self):
        schema = Schema('integer', enum=[1, 2, 3])
        value = '123'

        with pytest.raises(UnmarshalError):
            schema.unmarshal(value)

    def test_integer_enum(self):
        schema = Schema('integer', enum=[1, 2, 3])
        value = 2

        result = schema.unmarshal(value)

        assert result == int(value)

    def test_integer_enum_string_invalid(self):
        schema = Schema('integer', enum=[1, 2, 3])
        value = '2'

        with pytest.raises(UnmarshalError):
            schema.unmarshal(value)

    def test_integer_default(self):
        default_value = 123
        schema = Schema('integer', default=default_value)
        value = NoValue

        result = schema.unmarshal(value)

        assert result == default_value

    def test_integer_default_nullable(self):
        default_value = 123
        schema = Schema('integer', default=default_value, nullable=True)
        value = None

        result = schema.unmarshal(value)

        assert result is None

    def test_integer_invalid(self):
        schema = Schema('integer')
        value = 'abc'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_array_valid(self):
        schema = Schema('array', items=Schema('integer'))
        value = [1, 2, 3]

        result = schema.unmarshal(value)

        assert result == value

    def test_array_of_string_string_invalid(self):
        schema = Schema('array', items=Schema('string'))
        value = '123'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_array_of_integer_string_invalid(self):
        schema = Schema('array', items=Schema('integer'))
        value = '123'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_boolean_valid(self):
        schema = Schema('boolean')
        value = True

        result = schema.unmarshal(value)

        assert result == value

    def test_boolean_string_invalid(self):
        schema = Schema('boolean')
        value = 'True'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_number_valid(self):
        schema = Schema('number')
        value = 1.23

        result = schema.unmarshal(value)

        assert result == value

    def test_number_string_invalid(self):
        schema = Schema('number')
        value = '1.23'

        with pytest.raises(InvalidSchemaValue):
            schema.unmarshal(value)

    def test_number_int(self):
        schema = Schema('number')
        value = 1
        result = schema.unmarshal(value)

        assert result == 1
        assert type(result) == int

    def test_number_float(self):
        schema = Schema('number')
        value = 1.2
        result = schema.unmarshal(value)

        assert result == 1.2
        assert type(result) == float

    def test_number_format_float(self):
        schema = Schema('number', schema_format='float')
        value = 1.2
        result = schema.unmarshal(value)

        assert result == 1.2

    def test_number_format_double(self):
        schema = Schema('number', schema_format='double')
        value = 1.2
        result = schema.unmarshal(value)

        assert result == 1.2

    def test_schema_any_one_of(self):
        schema = Schema(one_of=[
            Schema('string'),
            Schema('array', items=Schema('string')),
        ])
        assert schema.unmarshal(['hello']) == ['hello']

    def test_schema_any(self):
        schema = Schema()
        assert schema.unmarshal('string') == 'string'
