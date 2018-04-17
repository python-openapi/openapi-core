import mock
import pytest

from openapi_core.exceptions import InvalidValueType, InvalidValue
from openapi_core.schema.schemas.models import Schema


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

        with pytest.raises(InvalidValueType):
            schema.unmarshal(value)

    def test_string_default(self):
        default_value = 'default'
        schema = Schema('string', default=default_value)
        value = None

        with pytest.raises(InvalidValueType):
            schema.unmarshal(value)

    def test_string_default_nullable(self):
        default_value = 'default'
        schema = Schema('string', default=default_value, nullable=True)
        value = None

        result = schema.unmarshal(value)

        assert result == default_value

    def test_integer_valid(self):
        schema = Schema('integer')
        value = '123'

        result = schema.unmarshal(value)

        assert result == int(value)

    def test_integer_enum_invalid(self):
        schema = Schema('integer', enum=[1, 2, 3])
        value = '123'

        with pytest.raises(InvalidValue):
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

        with pytest.raises(InvalidValueType):
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

        with pytest.raises(InvalidValueType):
            schema.unmarshal(value)
