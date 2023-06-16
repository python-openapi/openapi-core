import pytest

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types import media_type_deserializers
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)


class TestMediaTypeDeserializer:
    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(
            media_type,
            media_type_deserializers=media_type_deserializers,
            extra_media_type_deserializers=None,
        ):
            return MediaTypeDeserializersFactory(
                media_type_deserializers,
            ).create(
                media_type,
                extra_media_type_deserializers=extra_media_type_deserializers,
            )

        return create_deserializer

    def test_unsupported(self, deserializer_factory):
        mimetype = "application/unsupported"
        deserializer = deserializer_factory(mimetype)
        value = ""

        with pytest.warns(UserWarning):
            result = deserializer.deserialize(value)

        assert result == value

    def test_no_deserializer(self, deserializer_factory):
        mimetype = "application/json"
        deserializer = deserializer_factory(
            mimetype, media_type_deserializers=None
        )
        value = "{}"

        with pytest.warns(UserWarning):
            result = deserializer.deserialize(value)

        assert result == value

    def test_json_empty(self, deserializer_factory):
        mimetype = "application/json"
        deserializer = deserializer_factory(mimetype)
        value = ""

        with pytest.raises(DeserializeError):
            deserializer.deserialize(value)

    def test_json_empty_object(self, deserializer_factory):
        mimetype = "application/json"
        deserializer = deserializer_factory(mimetype)
        value = "{}"

        result = deserializer.deserialize(value)

        assert result == {}

    def test_urlencoded_form_empty(self, deserializer_factory):
        mimetype = "application/x-www-form-urlencoded"
        deserializer = deserializer_factory(mimetype)
        value = ""

        result = deserializer.deserialize(value)

        assert result == {}

    def test_urlencoded_form_simple(self, deserializer_factory):
        mimetype = "application/x-www-form-urlencoded"
        deserializer = deserializer_factory(mimetype)
        value = "param1=test"

        result = deserializer.deserialize(value)

        assert result == {"param1": "test"}

    @pytest.mark.parametrize("value", [b"", ""])
    def test_data_form_empty(self, deserializer_factory, value):
        mimetype = "multipart/form-data"
        deserializer = deserializer_factory(mimetype)

        result = deserializer.deserialize(value)

        assert result == {}

    def test_data_form_simple(self, deserializer_factory):
        mimetype = "multipart/form-data"
        deserializer = deserializer_factory(mimetype)
        value = (
            b'Content-Type: multipart/form-data; boundary="'
            b'===============2872712225071193122=="\n'
            b"MIME-Version: 1.0\n\n"
            b"--===============2872712225071193122==\n"
            b"Content-Type: text/plain\nMIME-Version: 1.0\n"
            b'Content-Disposition: form-data; name="param1"\n\ntest\n'
            b"--===============2872712225071193122==--\n"
        )

        result = deserializer.deserialize(value)

        assert result == {"param1": b"test"}

    def test_custom_simple(self, deserializer_factory):
        deserialized = "x-custom"

        def custom_deserializer(value):
            return deserialized

        custom_mimetype = "application/custom"
        extra_media_type_deserializers = {
            custom_mimetype: custom_deserializer,
        }
        deserializer = deserializer_factory(
            custom_mimetype,
            extra_media_type_deserializers=extra_media_type_deserializers,
        )
        value = "{}"

        result = deserializer.deserialize(
            value,
        )

        assert result == deserialized
