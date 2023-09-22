import pytest

from openapi_core.deserializing.styles.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.spec.paths import Spec


class TestStyleDeserializer:
    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(param):
            return StyleDeserializersFactory().create(param)

        return create_deserializer

    def test_unsupported(self, deserializer_factory):
        spec = {"name": "param", "in": "header", "style": "unsupported"}
        param = Spec.from_dict(spec, validator=None)
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
        param = Spec.from_dict(spec, validator=None)
        deserializer = deserializer_factory(param)
        value = ""

        with pytest.raises(EmptyQueryParameterValue):
            deserializer.deserialize(value)

    def test_query_valid(self, deserializer_factory):
        spec = {
            "name": "param",
            "in": "query",
        }
        param = Spec.from_dict(spec, validator=None)
        deserializer = deserializer_factory(param)
        value = "test"

        result = deserializer.deserialize(value)

        assert result == value
