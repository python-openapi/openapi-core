"""OpenAPI core mediaTypes module"""
from six import iteritems

from openapi_core.schemas import SchemaFactory


class MediaType(object):
    """Represents an OpenAPI MediaType."""

    def __init__(self, content_type, schema=None):
        self.content_type = content_type
        self.schema = schema

    def unmarshal(self, value):
        if not self.schema:
            return value

        return self.schema.unmarshal(value)


class MediaTypeGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, content):
        for content_type, media_type in iteritems(content):
            schema_spec = media_type.get('schema')

            schema = None
            if schema_spec:
                schema = self._create_schema(schema_spec)

            yield content_type, MediaType(content_type, schema)

    def _create_schema(self, schema_spec):
        return SchemaFactory(self.dereferencer).create(schema_spec)
