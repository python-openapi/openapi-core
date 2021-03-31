import mock
import pytest

from openapi_core.schema.operations.models import Operation


class TestSchemas(object):

    @pytest.fixture
    def operation(self):
        parameters = {
            'parameter_1': mock.sentinel.parameter_1,
            'parameter_2': mock.sentinel.parameter_2,
        }
        return Operation('get', '/path', {}, parameters=parameters)

    def test_iteritems(self, operation):
        for name in operation.parameters:
            assert operation[name] == operation.parameters[name]
