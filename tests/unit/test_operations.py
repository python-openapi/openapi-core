import mock
import pytest

from openapi_core.operations import Operation


class TestSchemas(object):

    @pytest.fixture
    def oepration(self):
        parameters = {
            'parameter_1': mock.sentinel.parameter_1,
            'parameter_2': mock.sentinel.parameter_2,
        }
        return Operation('get', '/path', parameters=parameters)

    @property
    def test_iteritems(self, oepration):
        for name in oepration.parameters.keys():
            assert oepration[name] == oepration.parameters[name]
