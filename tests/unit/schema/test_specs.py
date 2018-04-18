import mock
import pytest

from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.paths.models import Path
from openapi_core.schema.specs.models import Spec


class TestSpecs(object):

    @pytest.fixture
    def path1(self):
        operations = {
            'get': mock.sentinel.path1_get,
        }
        return Path('path1', operations)

    @pytest.fixture
    def path2(self):
        operations = {
            'post': mock.sentinel.path2_psot,
        }
        return Path('path2', operations)

    @pytest.fixture
    def spec(self, path1, path2):
        servers = []
        paths = {
            '/path1': path1,
            '/path2': path2,
        }
        return Spec(servers, paths)

    def test_iteritems(self, spec):
        for path_name in spec.paths.keys():
            assert spec[path_name] ==\
                spec.paths[path_name]

    def test_valid(self, spec):
        operation = spec.get_operation('/path1', 'get')

        assert operation == mock.sentinel.path1_get

    def test_invalid_path(self, spec):
        with pytest.raises(InvalidOperation):
            spec.get_operation('/path3', 'get')

    def test_invalid_method(self, spec):
        with pytest.raises(InvalidOperation):
            spec.get_operation('/path1', 'post')
