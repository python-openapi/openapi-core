"""OpenAPI core request bodies factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.content.factories import ContentFactory
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.request_bodies.models import RequestBody


class RequestBodyFactory(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def create(self, request_body_spec):
        request_body_deref = self.dereferencer.dereference(
            request_body_spec)
        content_spec = request_body_deref['content']
        content = self.content_factory.create(content_spec)
        required = request_body_deref.get('required', False)

        extensions = self.extensions_generator.generate(request_body_deref)

        return RequestBody(
            content,
            required=required, extensions=extensions,
        )

    @property
    @lru_cache()
    def content_factory(self):
        return ContentFactory(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
