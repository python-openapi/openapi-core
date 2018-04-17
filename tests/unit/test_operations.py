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
        for name in operation.parameters.keys():
            assert operation[name] == operation.parameters[name]


class TestResponses(object):

    @pytest.fixture
    def operation(self):
        responses = {
            '200': mock.sentinel.response_200,
            '299': mock.sentinel.response_299,
            '2XX': mock.sentinel.response_2XX,
            'default': mock.sentinel.response_default,
        }
        return Operation('get', '/path', responses, parameters={})

    def test_default(self, operation):
        response = operation.get_response()

        assert response == operation.responses['default']

    def test_range(self, operation):
        response = operation.get_response('201')

        assert response == operation.responses['2XX']

    def test_exact(self, operation):
        response = operation.get_response('200')

        assert response == operation.responses['200']
