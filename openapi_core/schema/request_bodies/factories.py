"""OpenAPI core request bodies factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.media_types.generators import MediaTypeGenerator
from openapi_core.schema.request_bodies.models import RequestBody


class RequestBodyFactory(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def create(self, request_body_spec):
        request_body_deref = self.dereferencer.dereference(
            request_body_spec)
        content = request_body_deref['content']
        media_types = self.media_types_generator.generate(content)
        required = request_body_deref.get('required', False)
        return RequestBody(media_types, required=required)

    @property
    @lru_cache()
    def media_types_generator(self):
        return MediaTypeGenerator(self.dereferencer, self.schemas_registry)
