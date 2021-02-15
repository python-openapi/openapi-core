import datetime
import uuid

from isodate.tzinfo import UTC, FixedOffset
import pytest

from openapi_core.schema.media_types.models import MediaType
from openapi_core.schema.parameters.models import Parameter
from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.schemas.models import Schema
from openapi_core.schema.schemas.types import NoValue
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    InvalidSchemaFormatValue, InvalidSchemaValue, UnmarshalError,
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.util import build_format_checker


@pytest.fixture
def unmarshaller_factory():
    def create_unmarshaller(schema, custom_formatters=None, context=None):
        custom_formatters = custom_formatters or {}
        format_checker = build_format_checker(**custom_formatters)
        return SchemaUnmarshallersFactory(
            format_checker=format_checker,
            custom_formatters=custom_formatters, context=context).create(
                schema)
    return create_unmarshaller


class TestParameterUnmarshal(object):

    def test_no_schema(self, unmarshaller_factory):
        param = Parameter('param', 'query')
        value = 'test'

        with pytest.raises(TypeError):
            unmarshaller_factory(param.schema).unmarshal(value)

    def test_schema_type_invalid(self, unmarshaller_factory):
        schema = Schema('integer', _source={'type': 'integer'})
        param = Parameter('param', 'query', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(param.schema).unmarshal(value)

    def test_schema_custom_format_invalid(self, unmarshaller_factory):

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                raise ValueError
        formatter = CustomFormatter()
        custom_format = 'custom'
        custom_formatters = {
            custom_format: formatter,
        }
        schema = Schema(
            'string',
            schema_format=custom_format,
            _source={'type': 'string', 'format': 'custom'},
        )
        param = Parameter('param', 'query', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(
                param.schema,
                custom_formatters=custom_formatters,
            ).unmarshal(value)


class TestMediaTypeUnmarshal(object):

    def test_no_schema(self, unmarshaller_factory):
        media_type = MediaType('application/json')
        value = 'test'

        with pytest.raises(TypeError):
            unmarshaller_factory(media_type.schema).unmarshal(value)

    def test_schema_type_invalid(self, unmarshaller_factory):
        schema = Schema('integer', _source={'type': 'integer'})
        media_type = MediaType('application/json', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(media_type.schema).unmarshal(value)

    def test_schema_custom_format_invalid(self, unmarshaller_factory):

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                raise ValueError
        formatter = CustomFormatter()
        custom_format = 'custom'
        custom_formatters = {
            custom_format: formatter,
        }
        schema = Schema(
            'string',
            schema_format=custom_format,
            _source={'type': 'string', 'format': 'custom'},
        )
        media_type = MediaType('application/json', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(
                media_type.schema,
                custom_formatters=custom_formatters,
            ).unmarshal(value)


class TestSchemaUnmarshallerCall(object):

    def test_deprecated(self, unmarshaller_factory):
        schema = Schema('string', deprecated=True)
        value = 'test'

        with pytest.warns(DeprecationWarning):
            result = unmarshaller_factory(schema)(value)

        assert result == value

    @pytest.mark.parametrize('schema_type', [
        'boolean', 'array', 'integer', 'number',
    ])
    def test_non_string_empty_value(self, schema_type, unmarshaller_factory):
        schema = Schema(schema_type)
        value = ''

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_string_valid(self, unmarshaller_factory):
        schema = Schema('string')
        value = 'test'

        result = unmarshaller_factory(schema)(value)

        assert result == value

    def test_string_format_uuid_valid(self, unmarshaller_factory):
        schema = Schema(SchemaType.STRING, schema_format='uuid')
        value = str(uuid.uuid4())

        result = unmarshaller_factory(schema)(value)

        assert result == uuid.UUID(value)

    def test_string_format_uuid_uuid_quirks_invalid(
            self, unmarshaller_factory):
        schema = Schema(SchemaType.STRING, schema_format='uuid')
        value = uuid.uuid4()

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_string_format_password(self, unmarshaller_factory):
        schema = Schema(SchemaType.STRING, schema_format='password')
        value = 'password'

        result = unmarshaller_factory(schema)(value)

        assert result == 'password'

    def test_string_float_invalid(self, unmarshaller_factory):
        schema = Schema('string')
        value = 1.23

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_string_default(self, unmarshaller_factory):
        default_value = 'default'
        schema = Schema('string', default=default_value)
        value = NoValue

        result = unmarshaller_factory(schema)(value)

        assert result == default_value

    @pytest.mark.parametrize('default_value', ['default', None])
    def test_string_default_nullable(
            self, default_value, unmarshaller_factory):
        schema = Schema('string', default=default_value, nullable=True)
        value = NoValue

        result = unmarshaller_factory(schema)(value)

        assert result == default_value

    def test_string_format_date(self, unmarshaller_factory):
        schema = Schema('string', schema_format='date')
        value = '2018-01-02'

        result = unmarshaller_factory(schema)(value)

        assert result == datetime.date(2018, 1, 2)

    def test_string_format_datetime_invalid(self, unmarshaller_factory):
        schema = Schema('string', schema_format='date-time')
        value = '2018-01-02T00:00:00'

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_string_format_datetime_utc(self, unmarshaller_factory):
        schema = Schema('string', schema_format='date-time')
        value = '2018-01-02T00:00:00Z'

        result = unmarshaller_factory(schema)(value)

        tzinfo = UTC
        assert result == datetime.datetime(2018, 1, 2, 0, 0, tzinfo=tzinfo)

    def test_string_format_datetime_tz(self, unmarshaller_factory):
        schema = Schema('string', schema_format='date-time')
        value = '2020-04-01T12:00:00+02:00'

        result = unmarshaller_factory(schema)(value)

        tzinfo = FixedOffset(2)
        assert result == datetime.datetime(2020, 4, 1, 12, 0, 0, tzinfo=tzinfo)

    def test_string_format_custom(self, unmarshaller_factory):
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

        result = unmarshaller_factory(
            schema, custom_formatters=custom_formatters)(value)

        assert result == formatted

    def test_string_format_custom_value_error(self, unmarshaller_factory):

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
            unmarshaller_factory(schema, custom_formatters=custom_formatters)(
                value)

    def test_string_format_unknown(self, unmarshaller_factory):
        unknown_format = 'unknown'
        schema = Schema('string', schema_format=unknown_format)
        value = 'x'

        with pytest.raises(FormatterNotFoundError):
            unmarshaller_factory(schema)(value)

    def test_string_format_invalid_value(self, unmarshaller_factory):
        custom_format = 'custom'
        schema = Schema('string', schema_format=custom_format)
        value = 'x'

        with pytest.raises(
            FormatterNotFoundError,
            message=(
                'Formatter not found for custom format'
            ),
        ):
            unmarshaller_factory(schema)(value)

    def test_integer_valid(self, unmarshaller_factory):
        schema = Schema('integer')
        value = 123

        result = unmarshaller_factory(schema)(value)

        assert result == int(value)

    def test_integer_string_invalid(self, unmarshaller_factory):
        schema = Schema('integer')
        value = '123'

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_integer_enum_invalid(self, unmarshaller_factory):
        schema = Schema('integer', enum=[1, 2, 3])
        value = '123'

        with pytest.raises(UnmarshalError):
            unmarshaller_factory(schema)(value)

    def test_integer_enum(self, unmarshaller_factory):
        schema = Schema('integer', enum=[1, 2, 3])
        value = 2

        result = unmarshaller_factory(schema)(value)

        assert result == int(value)

    def test_integer_enum_string_invalid(self, unmarshaller_factory):
        schema = Schema('integer', enum=[1, 2, 3])
        value = '2'

        with pytest.raises(UnmarshalError):
            unmarshaller_factory(schema)(value)

    def test_integer_default(self, unmarshaller_factory):
        default_value = 123
        schema = Schema('integer', default=default_value)
        value = NoValue

        result = unmarshaller_factory(schema)(value)

        assert result == default_value

    def test_integer_default_nullable(self, unmarshaller_factory):
        default_value = 123
        schema = Schema('integer', default=default_value, nullable=True)
        value = None

        result = unmarshaller_factory(schema)(value)

        assert result is None

    def test_integer_invalid(self, unmarshaller_factory):
        schema = Schema('integer')
        value = 'abc'

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_array_valid(self, unmarshaller_factory):
        schema = Schema('array', items=Schema('integer'))
        value = [1, 2, 3]

        result = unmarshaller_factory(schema)(value)

        assert result == value

    def test_array_null(self, unmarshaller_factory):
        schema = Schema(
            'array',
            items=Schema('integer'),
        )
        value = None

        with pytest.raises(TypeError):
            unmarshaller_factory(schema)(value)

    def test_array_nullable(self, unmarshaller_factory):
        schema = Schema(
            'array',
            items=Schema('integer'),
            nullable=True,
        )
        value = None
        result = unmarshaller_factory(schema)(value)

        assert result is None

    def test_array_of_string_string_invalid(self, unmarshaller_factory):
        schema = Schema('array', items=Schema('string'))
        value = '123'

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_array_of_integer_string_invalid(self, unmarshaller_factory):
        schema = Schema('array', items=Schema('integer'))
        value = '123'

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_boolean_valid(self, unmarshaller_factory):
        schema = Schema('boolean')
        value = True

        result = unmarshaller_factory(schema)(value)

        assert result == value

    def test_boolean_string_invalid(self, unmarshaller_factory):
        schema = Schema('boolean')
        value = 'True'

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_number_valid(self, unmarshaller_factory):
        schema = Schema('number')
        value = 1.23

        result = unmarshaller_factory(schema)(value)

        assert result == value

    def test_number_string_invalid(self, unmarshaller_factory):
        schema = Schema('number')
        value = '1.23'

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_number_int(self, unmarshaller_factory):
        schema = Schema('number')
        value = 1
        result = unmarshaller_factory(schema)(value)

        assert result == 1
        assert type(result) == int

    def test_number_float(self, unmarshaller_factory):
        schema = Schema('number')
        value = 1.2
        result = unmarshaller_factory(schema)(value)

        assert result == 1.2
        assert type(result) == float

    def test_number_format_float(self, unmarshaller_factory):
        schema = Schema('number', schema_format='float')
        value = 1.2
        result = unmarshaller_factory(schema)(value)

        assert result == 1.2

    def test_number_format_double(self, unmarshaller_factory):
        schema = Schema('number', schema_format='double')
        value = 1.2
        result = unmarshaller_factory(schema)(value)

        assert result == 1.2

    def test_object_nullable(self, unmarshaller_factory):
        schema = Schema(
            'object',
            properties={
                'foo': Schema('object', nullable=True),
            },
        )
        value = {'foo': None}
        result = unmarshaller_factory(schema)(value)

        assert result == {'foo': None}

    def test_schema_any_one_of(self, unmarshaller_factory):
        schema = Schema(one_of=[
            Schema('string'),
            Schema('array', items=Schema('string')),
        ])
        assert unmarshaller_factory(schema)(['hello']) == ['hello']

    def test_schema_any_all_of(self, unmarshaller_factory):
        schema = Schema(all_of=[
            Schema('array', items=Schema('string')),
        ])
        assert unmarshaller_factory(schema)(['hello']) == ['hello']

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
    def test_schema_any_all_of_invalid_properties(
            self, value, unmarshaller_factory):
        schema = Schema(
            all_of=[
                Schema(
                    'object',
                    required=['somestr'],
                    properties={
                        'somestr': Schema('string'),
                    },
                ),
                Schema(
                    'object',
                    required=['someint'],
                    properties={
                        'someint': Schema('integer'),
                    },
                ),
            ],
            additional_properties=False,
        )

        with pytest.raises(InvalidSchemaValue):
            unmarshaller_factory(schema)(value)

    def test_schema_any_all_of_any(self, unmarshaller_factory):
        schema = Schema(all_of=[
            Schema(),
            Schema('string', schema_format='date'),
        ])
        value = '2018-01-02'

        result = unmarshaller_factory(schema)(value)

        assert result == datetime.date(2018, 1, 2)

    def test_schema_any(self, unmarshaller_factory):
        schema = Schema()
        assert unmarshaller_factory(schema)('string') == 'string'

    @pytest.mark.parametrize('value', [
        {'additional': 1},
        {'foo': 'bar', 'bar': 'foo'},
        {'additional': {'bar': 1}},
    ])
    @pytest.mark.parametrize('additional_properties', [True, Schema()])
    def test_schema_free_form_object(
            self, value, additional_properties, unmarshaller_factory):
        schema = Schema('object', additional_properties=additional_properties)

        result = unmarshaller_factory(schema)(value)
        assert result == value

    def test_read_only_properties(self, unmarshaller_factory):
        id_property = Schema('integer', read_only=True)

        def properties():
            yield ('id', id_property)

        obj_schema = Schema('object', properties=properties(), required=['id'])

        # readOnly properties may be admitted in a Response context
        result = unmarshaller_factory(
            obj_schema, context=UnmarshalContext.RESPONSE)({"id": 10})
        assert result == {
            'id': 10,
        }

        # readOnly properties are not admitted on a Request context
        result = unmarshaller_factory(
            obj_schema, context=UnmarshalContext.REQUEST)({"id": 10})

        assert result == {}

    def test_write_only_properties(self, unmarshaller_factory):
        id_property = Schema('integer', write_only=True)

        def properties():
            yield ('id', id_property)

        obj_schema = Schema('object', properties=properties(), required=['id'])

        # readOnly properties may be admitted in a Response context
        result = unmarshaller_factory(
            obj_schema, context=UnmarshalContext.REQUEST)({"id": 10})
        assert result == {
            'id': 10,
        }

        # readOnly properties are not admitted on a Request context
        result = unmarshaller_factory(
            obj_schema, context=UnmarshalContext.RESPONSE)({"id": 10})

        assert result == {}
