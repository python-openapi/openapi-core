import mock
import pytest

from openapi_core.specs import Spec


class TestSpecs(object):

    @pytest.fixture
    def spec(self):
        servers = []
        paths = {
            'get': mock.sentinel.get,
            'post': mock.sentinel.post,
        }
        return Spec(servers, paths)

    @property
    def test_iteritems(self, spec):
        for path_name in spec.paths.keys():
            assert spec[path_name] ==\
                spec.paths[path_name]
