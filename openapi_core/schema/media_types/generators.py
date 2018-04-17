"""OpenAPI core media types generators module"""
from six import iteritems

from openapi_core.schema.media_types.models import MediaType


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
