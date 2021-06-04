import pytest

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)


class TestMediaTypeDeserializer:

    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(media_type, custom_deserializers=None):
            return MediaTypeDeserializersFactory(
                custom_deserializers=custom_deserializers).create(media_type)
        return create_deserializer

    def test_unsupported(self, deserializer_factory):
        mimetype = 'application/unsupported'
        value = ''

        with pytest.warns(UserWarning):
            result = deserializer_factory(mimetype)(value)

        assert result == value

    def test_json_empty(self, deserializer_factory):
        mimetype = 'application/json'
        value = ''

        with pytest.raises(DeserializeError):
            deserializer_factory(mimetype)(value)

    def test_json_empty_object(self, deserializer_factory):
        mimetype = 'application/json'
        value = "{}"

        result = deserializer_factory(mimetype)(value)

        assert result == {}

    def test_urlencoded_form_empty(self, deserializer_factory):
        mimetype = 'application/x-www-form-urlencoded'
        value = ''

        result = deserializer_factory(mimetype)(value)

        assert result == {}

    def test_urlencoded_form_simple(self, deserializer_factory):
        mimetype = 'application/x-www-form-urlencoded'
        value = 'param1=test'

        result = deserializer_factory(mimetype)(value)

        assert result == {'param1': 'test'}

    @pytest.mark.parametrize('value', [b'', ''])
    def test_data_form_empty(self, deserializer_factory, value):
        mimetype = 'multipart/form-data'

        result = deserializer_factory(mimetype)(value)

        assert result == {}

    def test_data_form_simple(self, deserializer_factory):
        mimetype = 'multipart/form-data'
        value = (
            b'Content-Type: multipart/form-data; boundary="'
            b'===============2872712225071193122=="\n'
            b'MIME-Version: 1.0\n\n'
            b'--===============2872712225071193122==\n'
            b'Content-Type: text/plain\nMIME-Version: 1.0\n'
            b'Content-Disposition: form-data; name="param1"\n\ntest\n'
            b'--===============2872712225071193122==--\n'
        )

        result = deserializer_factory(mimetype)(value)

        assert result == {'param1': b'test'}

    def test_custom_simple(self, deserializer_factory):
        custom_mimetype = 'application/custom'
        value = "{}"

        def custom_deserializer(value):
            return 'custom'
        custom_deserializers = {
            custom_mimetype: custom_deserializer,
        }

        result = deserializer_factory(
            custom_mimetype, custom_deserializers=custom_deserializers)(value)

        assert result == 'custom'
