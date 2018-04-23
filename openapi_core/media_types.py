"""OpenAPI core mediaTypes module"""
from collections import defaultdict

from json import loads
from six import iteritems

from openapi_core.exceptions import InvalidValueType, InvalidMediaTypeValue


MEDIA_TYPE_DESERIALIZERS = {
    'application/json': loads,
}


class MediaType(object):
    """Represents an OpenAPI MediaType."""

    def __init__(self, mimetype, schema=None):
        self.mimetype = mimetype
        self.schema = schema

    def get_deserializer_mapping(self):
        mapping = MEDIA_TYPE_DESERIALIZERS.copy()
        return defaultdict(lambda: lambda x: x, mapping)

    def get_dererializer(self):
        mapping = self.get_deserializer_mapping()
        return mapping[self.mimetype]

    def deserialize(self, value):
        deserializer = self.get_dererializer()
        return deserializer(value)

    def unmarshal(self, value):
        if not self.schema:
            return value

        try:
            deserialized = self.deserialize(value)
        except ValueError as exc:
            raise InvalidMediaTypeValue(str(exc))

        try:
            return self.schema.unmarshal(deserialized)
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
