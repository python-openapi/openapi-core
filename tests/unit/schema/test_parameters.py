import pytest

from openapi_core.schema.parameters.exceptions import (
    EmptyParameterValue, InvalidParameterValue,
)
from openapi_core.schema.parameters.enums import ParameterStyle
from openapi_core.schema.parameters.models import Parameter
from openapi_core.schema.schemas.models import Schema


class TestParameterInit(object):

    def test_path(self):
        param = Parameter('param', 'path')

        assert param.allow_empty_value is False
        assert param.style == ParameterStyle.SIMPLE
        assert param.explode is False

    def test_query(self):
        param = Parameter('param', 'query')

        assert param.allow_empty_value is False
        assert param.style == ParameterStyle.FORM
        assert param.explode is True

    def test_header(self):
        param = Parameter('param', 'header')

        assert param.allow_empty_value is False
        assert param.style == ParameterStyle.SIMPLE
        assert param.explode is False

    def test_cookie(self):
        param = Parameter('param', 'cookie')

        assert param.allow_empty_value is False
        assert param.style == ParameterStyle.FORM
        assert param.explode is True


class TestParameterCast(object):

    def test_deprecated(self):
        param = Parameter('param', 'query', deprecated=True)
        value = 'test'

        with pytest.warns(DeprecationWarning):
            result = param.cast(value)

        assert result == value

    def test_query_empty(self):
        param = Parameter('param', 'query')
        value = ''

        with pytest.raises(EmptyParameterValue):
            param.cast(value)

    def test_query_valid(self):
        param = Parameter('param', 'query')
        value = 'test'

        result = param.cast(value)

        assert result == value


class TestParameterUnmarshal(object):

    def test_query_valid(self):
        param = Parameter('param', 'query')
        value = 'test'

        result = param.unmarshal(value)

        assert result == value

    def test_query_allow_empty_value(self):
        param = Parameter('param', 'query', allow_empty_value=True)
        value = ''

        result = param.unmarshal(value)

        assert result == value

    def test_query_schema_type_invalid(self):
        schema = Schema('integer', _source={'type': 'integer'})
        param = Parameter('param', 'query', schema=schema)
        value = 'test'

        with pytest.raises(InvalidParameterValue):
            param.unmarshal(value)

    def test_query_schema_custom_format_invalid(self):
        def custom_formatter(value):
            raise ValueError
        schema = Schema(
            'string',
            schema_format='custom',
            _source={'type': 'string', 'format': 'custom'},
        )
        custom_formatters = {
            'custom': custom_formatter,
        }
        param = Parameter('param', 'query', schema=schema)
        value = 'test'

        with pytest.raises(InvalidParameterValue):
            param.unmarshal(value, custom_formatters=custom_formatters)
