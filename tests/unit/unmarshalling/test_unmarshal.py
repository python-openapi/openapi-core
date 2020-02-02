import pytest

from openapi_core.schema.media_types.models import MediaType
from openapi_core.schema.parameters.models import Parameter
from openapi_core.schema.schemas.models import Schema
from openapi_core.unmarshalling.schemas.exceptions import (
    InvalidSchemaFormatValue,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter


@pytest.fixture
def unmarshaller_factory():
    def create_unmarshaller(param_or_media_type, custom_formatters=None):
        return SchemaUnmarshallersFactory(
            custom_formatters=custom_formatters).create(
                param_or_media_type.schema)
    return create_unmarshaller


class TestParameterUnmarshal(object):

    def test_no_schema(self, unmarshaller_factory):
        param = Parameter('param', 'query')
        value = 'test'

        with pytest.raises(TypeError):
            unmarshaller_factory(param).unmarshal(value)

    def test_schema_type_invalid(self, unmarshaller_factory):
        schema = Schema('integer', _source={'type': 'integer'})
        param = Parameter('param', 'query', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(param).unmarshal(value)

    def test_schema_custom_format_invalid(self, unmarshaller_factory):

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                raise ValueError
        formatter = CustomFormatter()
        custom_format = 'custom'
        custom_formatters = {
            custom_format: formatter,
        }
        schema = Schema(
            'string',
            schema_format=custom_format,
            _source={'type': 'string', 'format': 'custom'},
        )
        param = Parameter('param', 'query', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(
                param, custom_formatters=custom_formatters).unmarshal(value)


class TestMediaTypeUnmarshal(object):

    def test_no_schema(self, unmarshaller_factory):
        media_type = MediaType('application/json')
        value = 'test'

        with pytest.raises(TypeError):
            unmarshaller_factory(media_type).unmarshal(value)

    def test_schema_type_invalid(self, unmarshaller_factory):
        schema = Schema('integer', _source={'type': 'integer'})
        media_type = MediaType('application/json', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(media_type).unmarshal(value)

    def test_schema_custom_format_invalid(self, unmarshaller_factory):

        class CustomFormatter(Formatter):
            def unmarshal(self, value):
                raise ValueError
        formatter = CustomFormatter()
        custom_format = 'custom'
        custom_formatters = {
            custom_format: formatter,
        }
        schema = Schema(
            'string',
            schema_format=custom_format,
            _source={'type': 'string', 'format': 'custom'},
        )
        media_type = MediaType('application/json', schema=schema)
        value = 'test'

        with pytest.raises(InvalidSchemaFormatValue):
            unmarshaller_factory(
                media_type, custom_formatters=custom_formatters).unmarshal(
                    value)
