import pytest

from openapi_core.deserializing.parameters.factories import (
    ParameterDeserializersFactory,
)
from openapi_core.deserializing.parameters.exceptions import (
    EmptyParameterValue,
)
from openapi_core.schema.parameters.models import Parameter


class TestParameterDeserializer(object):

    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(param):
            return ParameterDeserializersFactory().create(param)
        return create_deserializer

    def test_deprecated(self, deserializer_factory):
        param = Parameter('param', 'query', deprecated=True)
        value = 'test'

        with pytest.warns(DeprecationWarning):
            result = deserializer_factory(param)(value)

        assert result == value

    def test_query_empty(self, deserializer_factory):
        param = Parameter('param', 'query')
        value = ''

        with pytest.raises(EmptyParameterValue):
            deserializer_factory(param)(value)

    def test_query_valid(self, deserializer_factory):
        param = Parameter('param', 'query')
        value = 'test'

        result = deserializer_factory(param)(value)

        assert result == value
