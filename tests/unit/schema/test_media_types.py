import pytest

from openapi_core.schema.media_types.exceptions import InvalidMediaTypeValue
from openapi_core.schema.media_types.models import MediaType


class TestMediaTypeDeserialise(object):

    def test_empty(self):
        media_type = MediaType('application/json')
        value = ''

        with pytest.raises(InvalidMediaTypeValue):
            media_type.deserialise(value)

    def test_no_schema_deserialised(self):
        media_type = MediaType('application/json')
        value = "{}"

        result = media_type.deserialise(value)

        assert result == {}
