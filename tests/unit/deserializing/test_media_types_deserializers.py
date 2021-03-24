from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart

import pytest

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.schema.media_types.models import MediaType


class MIMEFormdata(MIMENonMultipart):
    def __init__(self, keyname, *args, **kwargs):
        super(MIMEFormdata, self).__init__(*args, **kwargs)
        self.add_header(
            "Content-Disposition", "form-data; name=\"%s\"" % keyname)


def encode_multipart_formdata(fields):
    m = MIMEMultipart("form-data")

    for field, value in fields.items():
        data = MIMEFormdata(field, "text", "plain")
        data.set_payload(value)
        m.attach(data)

    return m


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

    def test_urlencoded_form_empty(self, deserializer_factory):
        media_type = MediaType('application/x-www-form-urlencoded')
        value = ''

        result = deserializer_factory(media_type)(value)

        assert result == {}

    def test_urlencoded_form_simple(self, deserializer_factory):
        media_type = MediaType('application/x-www-form-urlencoded')
        value = 'param1=test'

        result = deserializer_factory(media_type)(value)

        assert result == {'param1': 'test'}

    @pytest.mark.parametrize('value', [b'', ''])
    def test_data_form_empty(self, deserializer_factory, value):
        media_type = MediaType('multipart/form-data')

        result = deserializer_factory(media_type)(value)

        assert result == {}

    def test_data_form_simple(self, deserializer_factory):
        media_type = MediaType('multipart/form-data')
        formdata = encode_multipart_formdata({'param1': 'test'})
        value = str(formdata)

        result = deserializer_factory(media_type)(value)

        assert result == {'param1': b'test'}

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
