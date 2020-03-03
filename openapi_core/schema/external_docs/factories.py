"""OpenAPI core external docs factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.external_docs.models import ExternalDocumentation


class ExternalDocumentationFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, external_doc_spec):
        url = external_doc_spec['url']
        description = external_doc_spec.get('description')

        extensions = self.extensions_generator.generate(external_doc_spec)

        return ExternalDocumentation(
            url,
            description=description, extensions=extensions,
        )

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
