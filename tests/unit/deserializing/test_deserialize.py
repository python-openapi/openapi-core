import pytest

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.parameters.factories import (
    ParameterDeserializersFactory,
)
from openapi_core.deserializing.parameters.exceptions import (
    EmptyParameterValue,
)
from openapi_core.schema.media_types.models import MediaType
from openapi_core.schema.parameters.models import Parameter


class TestParameterDeserialise(object):

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


class TestMediaTypeDeserialise(object):

    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(media_type):
            return MediaTypeDeserializersFactory().create(media_type)
        return create_deserializer

    def test_empty(self, deserializer_factory):
        media_type = MediaType('application/json')
        value = ''

        with pytest.raises(DeserializeError):
            deserializer_factory(media_type)(value)

    def test_no_schema_deserialised(self, deserializer_factory):
        media_type = MediaType('application/json')
        value = "{}"

        result = deserializer_factory(media_type)(value)

        assert result == {}
