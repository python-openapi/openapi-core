"""OpenAPI core external docs factories module"""
from openapi_core.schema.external_docs.models import ExternalDocumentation


class ExternalDocumentationFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, external_doc_spec):
        url = external_doc_spec['url']
        description = external_doc_spec.get('description')

        return ExternalDocumentation(url, description=description)
