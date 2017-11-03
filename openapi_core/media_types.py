"""OpenAPI core mediaTypes module"""
from six import iteritems

from openapi_core.exceptions import InvalidValueType, InvalidMediaTypeValue


class MediaType(object):
    """Represents an OpenAPI MediaType."""

    def __init__(self, mimetype, schema=None):
        self.mimetype = mimetype
        self.schema = schema

    def unmarshal(self, value):
        if not self.schema:
            return value

        try:
            return self.schema.unmarshal(value)
        except InvalidValueType as exc:
            raise InvalidMediaTypeValue(str(exc))


class MediaTypeGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, content):
        for mimetype, media_type in iteritems(content):
            schema_spec = media_type.get('schema')

            schema = None
            if schema_spec:
                schema, _ = self.schemas_registry.get_or_create(schema_spec)

            yield mimetype, MediaType(mimetype, schema)
