"""OpenAPI core properties generators module"""
from six import iteritems


class PropertiesGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, properties):
        for property_name, schema_spec in iteritems(properties):
            schema = self._create_schema(schema_spec)
            yield property_name, schema

    def _create_schema(self, schema_spec):
        schema, _ = self.schemas_registry.get_or_create(schema_spec)
        return schema
