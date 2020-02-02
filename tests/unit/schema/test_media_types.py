from openapi_core.schema.media_types.models import MediaType


class TestMediaTypeCast(object):

    def test_empty(self):
        media_type = MediaType('application/json')
        value = ''

        result = media_type.cast(value)

        assert result == value
