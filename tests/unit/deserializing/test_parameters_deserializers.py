import pytest

from openapi_core.deserializing.parameters.factories import (
    ParameterDeserializersFactory,
)
from openapi_core.deserializing.parameters.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.spec.paths import SpecPath


class TestParameterDeserializer:

    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(param):
            return ParameterDeserializersFactory().create(param)
        return create_deserializer

    def test_unsupported(self, deserializer_factory):
        spec = {
            'name': 'param',
            'in': 'header',
            'style': 'unsupported'
        }
        param = SpecPath.from_spec(spec)
        value = ''

        with pytest.warns(UserWarning):
            result = deserializer_factory(param)(value)

        assert result == value

    def test_query_empty(self, deserializer_factory):
        spec = {
            'name': 'param',
            'in': 'query',
        }
        param = SpecPath.from_spec(spec)
        value = ''

        with pytest.raises(EmptyQueryParameterValue):
            deserializer_factory(param)(value)

    def test_query_valid(self, deserializer_factory):
        spec = {
            'name': 'param',
            'in': 'query',
        }
        param = SpecPath.from_spec(spec)
        value = 'test'

        result = deserializer_factory(param)(value)

        assert result == value
