import pytest

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.schema.media_types.models import MediaType


class TestMediaTypeDeserializer(object):

    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(media_type, custom_deserializers=None):
            return MediaTypeDeserializersFactory(
                custom_deserializers=custom_deserializers).create(media_type)
        return create_deserializer

    def test_json_empty(self, deserializer_factory):
        media_type = MediaType('application/json')
        value = ''

        with pytest.raises(DeserializeError):
            deserializer_factory(media_type)(value)

    def test_json_empty_object(self, deserializer_factory):
        media_type = MediaType('application/json')
        value = "{}"

        result = deserializer_factory(media_type)(value)

        assert result == {}

    def test_form_urlencoded_empty(self, deserializer_factory):
        media_type = MediaType('application/x-www-form-urlencoded')
        value = ''

        result = deserializer_factory(media_type)(value)

        assert result == {}

    def test_form_urlencoded_simple(self, deserializer_factory):
        media_type = MediaType('application/x-www-form-urlencoded')
        value = 'param1=test'

        result = deserializer_factory(media_type)(value)

        assert result == {'param1': 'test'}

    def test_custom_simple(self, deserializer_factory):
        custom_mimetype = 'application/custom'
        media_type = MediaType(custom_mimetype)
        value = "{}"

        def custom_deserializer(value):
            return 'custom'
        custom_deserializers = {
            custom_mimetype: custom_deserializer,
        }

        result = deserializer_factory(
            media_type, custom_deserializers=custom_deserializers)(value)

        assert result == 'custom'
