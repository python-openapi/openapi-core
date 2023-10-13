import pytest
from jsonschema_path import SchemaPath

from openapi_core.deserializing.styles.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)


class TestStyleDeserializer:
    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(param):
            return StyleDeserializersFactory().create(param)

        return create_deserializer

    def test_unsupported(self, deserializer_factory):
        spec = {"name": "param", "in": "header", "style": "unsupported"}
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        value = ""

        with pytest.warns(UserWarning):
            result = deserializer.deserialize(value)

        assert result == value

    def test_query_empty(self, deserializer_factory):
        spec = {
            "name": "param",
            "in": "query",
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        value = ""

        with pytest.raises(EmptyQueryParameterValue):
            deserializer.deserialize(value)

    def test_query_valid(self, deserializer_factory):
        spec = {
            "name": "param",
            "in": "query",
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        value = "test"

        result = deserializer.deserialize(value)

        assert result == value
