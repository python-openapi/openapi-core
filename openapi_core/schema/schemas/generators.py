"""OpenAPI core schemas generators module"""
import logging

from six import iteritems

log = logging.getLogger(__name__)


class SchemasGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, schemas_spec):
        schemas_deref = self.dereferencer.dereference(schemas_spec)

        for schema_name, schema_spec in iteritems(schemas_deref):
            schema, _ = self.schemas_registry.get_or_create(schema_spec)
            yield schema_name, schema
