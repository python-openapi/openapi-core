import pytest

from jsonschema.validators import RefResolver
from openapi_spec_validator.validators import Dereferencer
from openapi_spec_validator import default_handlers

from openapi_core.schema.schemas.registries import SchemaRegistry


class TestSchemaRegistryGetOrCreate(object):

    @pytest.fixture
    def schema_dict(self):
        return {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                },
                'suberror': {
                    '$ref': '#/components/schemas/Error',
                },
                'suberrors': {
                    'items': {
                        '$ref': '#/components/schemas/Error'
                    },
                    'type': 'array'
                }
            },
        }

    @pytest.fixture
    def spec_dict(self, schema_dict):
        return {
            'components': {
                'schemas': {
                    'Error': schema_dict,
                },
            },
        }

    @pytest.fixture
    def dereferencer(self, spec_dict):
        spec_resolver = RefResolver('', spec_dict, handlers=default_handlers)
        return Dereferencer(spec_resolver)

    @pytest.fixture
    def schemas_registry(self, dereferencer):
        return SchemaRegistry(dereferencer)

    def test_recursion(self, schemas_registry, schema_dict):
        schema, _ = schemas_registry.get_or_create(schema_dict)

        assert schema.properties['suberror'] ==\
            schema.properties['suberror'].properties['suberror']

    def test_array_recursion(self, schemas_registry, schema_dict):
        schema, _ = schemas_registry.get_or_create(schema_dict)

        assert schema.properties['suberrors'].items ==\
            schema.properties['suberrors'].items.properties['suberrors'].items
