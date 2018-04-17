import mock
import pytest

from openapi_core.schema.paths.models import Path


class TestPaths(object):

    @pytest.fixture
    def path(self):
        operations = {
            'get': mock.sentinel.get,
            'post': mock.sentinel.post,
        }
        return Path('/path', operations)

    @property
    def test_iteritems(self, path):
        for http_method in path.operations.keys():
            assert path[http_method] ==\
                path.operations[http_method]
