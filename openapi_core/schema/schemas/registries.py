"""OpenAPI core schemas registries module"""
import logging

from openapi_core.schema.schemas.factories import SchemaFactory

log = logging.getLogger(__name__)


class SchemaRegistry(SchemaFactory):

    def __init__(self, dereferencer):
        super(SchemaRegistry, self).__init__(dereferencer)
        self._schemas = {}

    def get_or_create(self, schema_spec):
        schema_deref = self.dereferencer.dereference(schema_spec)
        model = schema_deref.get('x-model', None)

        if model and model in self._schemas:
            return self._schemas[model], False

        return self.create(schema_deref), True
