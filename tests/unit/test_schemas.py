import mock
import pytest

from openapi_core.schemas import Schema


class TestSchemas(object):

    @pytest.fixture
    def schema(self):
        properties = {
            'application/json': mock.sentinel.application_json,
            'text/csv': mock.sentinel.text_csv,
        }
        return Schema('object', properties=properties)

    @property
    def test_iteritems(self, schema):
        for name in schema.properties.keys():
            assert schema[name] == schema.properties[name]
