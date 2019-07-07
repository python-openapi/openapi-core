import pytest

from jsonschema.validators import RefResolver
from openapi_spec_validator.validators import Dereferencer
from openapi_spec_validator import default_handlers

from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.schemas.registries import SchemaRegistry


class BaseTestRegistry(object):

    @pytest.fixture
    def dereferencer(self, spec_dict):
        spec_resolver = RefResolver('', spec_dict, handlers=default_handlers)
        return Dereferencer(spec_resolver)

    @pytest.fixture
    def schemas_registry(self, dereferencer):
        return SchemaRegistry(dereferencer)


class TestSchemaRegistryGetOrCreate(BaseTestRegistry):

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

    def test_recursion(self, schemas_registry, schema_dict):
        schema, _ = schemas_registry.get_or_create(schema_dict)

        assert schema.properties['suberror'] ==\
            schema.properties['suberror'].properties['suberror']


class TestAllOf(BaseTestRegistry):

        @pytest.fixture
        def schema_dict(self):
            return {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                    },
                    'suberror': {
                        'allOf': [
                            {'$ref': '#/components/schemas/Error'},
                            {'$ref': '#/components/schemas/TS'}
                        ]
                    }
                },
            }

        @pytest.fixture
        def spec_dict(self, schema_dict):
            return {
                'components': {
                    'schemas': {
                        'Error': {
                            'type': 'object',
                            'properties': {
                                'message': {
                                    'type': 'string'
                                },
                            }
                        },
                        'TS': {
                            'type': 'object',
                            'properties': {
                                'moment': {
                                    'type': 'string',
                                    'format': 'datetime'
                                }
                            }
                        }
                    }
                }
            }


        def test_all_of_intrinsic_type(self, schemas_registry, schema_dict):
            schema, _ = schemas_registry.get_or_create(schema_dict)

            suberror = schema.properties['suberror']
            assert suberror.type == SchemaType.OBJECT
