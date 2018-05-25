import pytest

from openapi_core.schema.parameters.exceptions import EmptyParameterValue
from openapi_core.schema.parameters.enums import ParameterStyle
from openapi_core.schema.parameters.models import Parameter


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


class TestParameterUnmarshal(object):

    def test_deprecated(self):
        param = Parameter('param', 'query', deprecated=True)
        value = 'test'

        with pytest.warns(DeprecationWarning):
            result = param.unmarshal(value)

        assert result == value

    def test_query_valid(self):
        param = Parameter('param', 'query')
        value = 'test'

        result = param.unmarshal(value)

        assert result == value

    def test_query_empty(self):
        param = Parameter('param', 'query')
        value = ''

        with pytest.raises(EmptyParameterValue):
            param.unmarshal(value)

    def test_query_allow_empty_value(self):
        param = Parameter('param', 'query', allow_empty_value=True)
        value = ''

        result = param.unmarshal(value)

        assert result == value
