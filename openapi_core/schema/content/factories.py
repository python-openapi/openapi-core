"""OpenAPI core content factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.content.models import Content
from openapi_core.schema.media_types.generators import MediaTypeGenerator


class ContentFactory(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def create(self, content_spec):
        media_types = self.media_types_generator.generate(content_spec)

        return Content(media_types)

    @property
    @lru_cache()
    def media_types_generator(self):
        return MediaTypeGenerator(self.dereferencer, self.schemas_registry)
