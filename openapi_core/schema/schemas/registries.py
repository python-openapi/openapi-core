"""OpenAPI core schemas registries module"""
import logging

from lazy_object_proxy import Proxy

from openapi_core.schema.schemas.factories import SchemaFactory
from openapi_core.schema.schemas.util import dicthash

log = logging.getLogger(__name__)


class SchemaRegistry(SchemaFactory):

    def __init__(self, dereferencer):
        super(SchemaRegistry, self).__init__(dereferencer)
        self._schemas = {}

    def get_or_create(self, schema_spec):
        schema_hash = dicthash(schema_spec)
        schema_deref = self.dereferencer.dereference(schema_spec)

        if schema_hash in self._schemas:
            return self._schemas[schema_hash], False

        if '$ref' in schema_spec:
            schema = Proxy(lambda: self.create(schema_deref))
        else:
            schema = self.create(schema_deref)

        self._schemas[schema_hash] = schema

        return schema, True
