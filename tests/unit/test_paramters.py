import pytest

from openapi_core.exceptions import EmptyValue
from openapi_core.parameters import Parameter


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

        with pytest.raises(EmptyValue):
            param.unmarshal(value)

    def test_query_allow_empty_value(self):
        param = Parameter('param', 'query', allow_empty_value=True)
        value = ''

        result = param.unmarshal(value)

        assert result == value
