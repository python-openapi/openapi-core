"""OpenAPI core media types generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.media_types.models import MediaType


class MediaTypeGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, content):
        for mimetype, media_type in iteritems(content):
            schema_spec = media_type.get('schema')

            example_spec = media_type.get('example')
            example_type = type(example_spec)
            if example_type is dict:
                example = self.dereferencer.dereference(example_spec)
            else:
                example = example_spec

            extensions = self.extensions_generator.generate(media_type)

            schema = None
            if schema_spec:
                schema, _ = self.schemas_registry.get_or_create(schema_spec)

            yield mimetype, MediaType(
                mimetype,
                schema=schema, example=example, extensions=extensions,
            )

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
