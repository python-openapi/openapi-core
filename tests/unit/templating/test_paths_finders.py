import pytest

from openapi_core.schema.infos.models import Info
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.parameters.models import Parameter
from openapi_core.schema.paths.models import Path
from openapi_core.schema.servers.models import Server, ServerVariable
from openapi_core.schema.specs.models import Spec
from openapi_core.templating.datatypes import TemplateResult
from openapi_core.templating.paths.exceptions import (
    PathNotFound, OperationNotFound, ServerNotFound,
)
from openapi_core.templating.paths.finders import PathFinder
from openapi_core.testing import MockRequest


class BaseTestSimpleServer(object):

    server_url = 'http://petstore.swagger.io'

    @pytest.fixture
    def server(self):
        return Server(self.server_url, {})

    @pytest.fixture
    def servers(self, server):
        return [server, ]


class BaseTestVariableServer(BaseTestSimpleServer):

    server_url = 'http://petstore.swagger.io/{version}'
    server_variable_name = 'version'
    server_variable_default = 'v1'
    server_variable_enum = ['v1', 'v2']

    @pytest.fixture
    def server_variable(self):
        return ServerVariable(
            self.server_variable_name,
            default=self.server_variable_default,
            enum=self.server_variable_enum,
        )

    @pytest.fixture
    def server_variables(self, server_variable):
        return {
            self.server_variable_name: server_variable,
        }

    @pytest.fixture
    def server(self, server_variables):
        return Server(self.server_url, server_variables)


class BaseTestSimplePath(object):

    path_name = '/resource'

    @pytest.fixture
    def path(self, operations):
        return Path(self.path_name, operations)

    @pytest.fixture
    def paths(self, path):
        return {
            self.path_name: path,
        }


class BaseTestVariablePath(BaseTestSimplePath):

    path_name = '/resource/{resource_id}'
    path_parameter_name = 'resource_id'

    @pytest.fixture
    def parameter(self):
        return Parameter(self.path_parameter_name, 'path')

    @pytest.fixture
    def parameters(self, parameter):
        return {
            self.path_parameter_name: parameter
        }

    @pytest.fixture
    def path(self, operations, parameters):
        return Path(self.path_name, operations, parameters=parameters)


class BaseTestSpecServer(object):

    @pytest.fixture
    def info(self):
        return Info('Test schema', '1.0')

    @pytest.fixture
    def operation(self):
        return Operation('get', self.path_name, {}, {})

    @pytest.fixture
    def operations(self, operation):
        return {
            'get': operation,
        }

    @pytest.fixture
    def spec(self, info, paths, servers):
        return Spec(info, paths, servers)

    @pytest.fixture
    def finder(self, spec):
        return PathFinder(spec)


class BaseTestPathServer(BaseTestSpecServer):

    @pytest.fixture
    def path(self, operations, servers):
        return Path(self.path_name, operations, servers=servers)

    @pytest.fixture
    def spec(self, info, paths):
        return Spec(info, paths)


class BaseTestOperationServer(BaseTestSpecServer):

    @pytest.fixture
    def operation(self, servers):
        return Operation('get', self.path_name, {}, {}, servers=servers)

    @pytest.fixture
    def spec(self, info, paths):
        return Spec(info, paths)


class BaseTestServerNotFound(object):

    @pytest.fixture
    def servers(self):
        return []

    def test_raises(self, finder):
        request_uri = '/resource'
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)

        with pytest.raises(ServerNotFound):
            finder.find(request)


class BaseTestOperationNotFound(object):

    @pytest.fixture
    def operations(self):
        return {}

    def test_raises(self, finder):
        request_uri = '/resource'
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)

        with pytest.raises(OperationNotFound):
            finder.find(request)


class BaseTestValid(object):

    def test_simple(self, finder, path, operation, server):
        request_uri = '/resource'
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)

        result = finder.find(request)

        path_result = TemplateResult(self.path_name, {})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path, operation, server, path_result, server_result,
        )


class BaseTestVariableValid(object):

    @pytest.mark.parametrize('version', ['v1', 'v2'])
    def test_variable(self, finder, path, operation, server, version):
        request_uri = '/{0}/resource'.format(version)
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)

        result = finder.find(request)

        path_result = TemplateResult(self.path_name, {})
        server_result = TemplateResult(self.server_url, {'version': version})
        assert result == (
            path, operation, server, path_result, server_result,
        )


class BaseTestPathVariableValid(object):

    @pytest.mark.parametrize('res_id', ['111', '222'])
    def test_path_variable(self, finder, path, operation, server, res_id):
        request_uri = '/resource/{0}'.format(res_id)
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)

        result = finder.find(request)

        path_result = TemplateResult(self.path_name, {'resource_id': res_id})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path, operation, server, path_result, server_result,
        )


class BaseTestPathNotFound(object):

    @pytest.fixture
    def paths(self):
        return {}

    def test_raises(self, finder):
        request_uri = '/resource'
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)

        with pytest.raises(PathNotFound):
            finder.find(request)


class TestSpecSimpleServerServerNotFound(
        BaseTestServerNotFound, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestSpecSimpleServerOperationNotFound(
        BaseTestOperationNotFound, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestSpecSimpleServerPathNotFound(
        BaseTestPathNotFound, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestOperationSimpleServerServerNotFound(
        BaseTestServerNotFound, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestOperationSimpleServerOperationNotFound(
        BaseTestOperationNotFound, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestOperationSimpleServerPathNotFound(
        BaseTestPathNotFound, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestPathSimpleServerServerNotFound(
        BaseTestServerNotFound, BaseTestPathServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestPathSimpleServerOperationNotFound(
        BaseTestOperationNotFound, BaseTestPathServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestPathSimpleServerPathNotFound(
        BaseTestPathNotFound, BaseTestPathServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestSpecSimpleServerValid(
        BaseTestValid, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestOperationSimpleServerValid(
        BaseTestValid, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestPathSimpleServerValid(
        BaseTestValid, BaseTestPathServer,
        BaseTestSimplePath, BaseTestSimpleServer):
    pass


class TestSpecSimpleServerVariablePathValid(
        BaseTestPathVariableValid, BaseTestSpecServer,
        BaseTestVariablePath, BaseTestSimpleServer):
    pass


class TestOperationSimpleServerVariablePathValid(
        BaseTestPathVariableValid, BaseTestOperationServer,
        BaseTestVariablePath, BaseTestSimpleServer):
    pass


class TestPathSimpleServerVariablePathValid(
        BaseTestPathVariableValid, BaseTestPathServer,
        BaseTestVariablePath, BaseTestSimpleServer):
    pass


class TestSpecVariableServerServerNotFound(
        BaseTestServerNotFound, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestSpecVariableServerOperationNotFound(
        BaseTestOperationNotFound, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestSpecVariableServerPathNotFound(
        BaseTestPathNotFound, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestOperationVariableServerServerNotFound(
        BaseTestServerNotFound, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestOperationVariableServerOperationNotFound(
        BaseTestOperationNotFound, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestOperationVariableServerPathNotFound(
        BaseTestPathNotFound, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestPathVariableServerServerNotFound(
        BaseTestServerNotFound, BaseTestPathServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestPathVariableServerOperationNotFound(
        BaseTestOperationNotFound, BaseTestPathServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestPathVariableServerPathNotFound(
        BaseTestPathNotFound, BaseTestPathServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestSpecVariableServerValid(
        BaseTestVariableValid, BaseTestSpecServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestOperationVariableServerValid(
        BaseTestVariableValid, BaseTestOperationServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestPathVariableServerValid(
        BaseTestVariableValid, BaseTestPathServer,
        BaseTestSimplePath, BaseTestVariableServer):
    pass


class TestSimilarPaths(
        BaseTestSpecServer, BaseTestSimpleServer):

    path_name = '/tokens'

    @pytest.fixture
    def operation_2(self):
        return Operation('get', '/keys/{id}/tokens', {}, {})

    @pytest.fixture
    def operations_2(self, operation_2):
        return {
            'get': operation_2,
        }

    @pytest.fixture
    def path(self, operations):
        return Path('/tokens', operations)

    @pytest.fixture
    def path_2(self, operations_2):
        return Path('/keys/{id}/tokens', operations_2)

    @pytest.fixture
    def paths(self, path, path_2):
        return {
            path.name: path,
            path_2.name: path_2,
        }

    def test_valid(self, finder, path_2, operation_2, server):
        token_id = '123'
        request_uri = '/keys/{0}/tokens'.format(token_id)
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)

        result = finder.find(request)

        path_result = TemplateResult(path_2.name, {'id': token_id})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path_2, operation_2, server, path_result, server_result,
        )


class TestConcretePaths(
        BaseTestSpecServer, BaseTestSimpleServer):

    path_name = '/keys/{id}/tokens'

    @pytest.fixture
    def operation_2(self):
        return Operation('get', '/keys/master/tokens', {}, {})

    @pytest.fixture
    def operations_2(self, operation_2):
        return {
            'get': operation_2,
        }

    @pytest.fixture
    def path(self, operations):
        return Path('/keys/{id}/tokens', operations)

    @pytest.fixture
    def path_2(self, operations_2):
        return Path('/keys/master/tokens', operations_2)

    @pytest.fixture
    def paths(self, path, path_2):
        return {
            path.name: path,
            path_2.name: path_2,
        }

    def test_valid(self, finder, path_2, operation_2, server):
        request_uri = '/keys/master/tokens'
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)
        result = finder.find(request)

        path_result = TemplateResult(path_2.name, {})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path_2, operation_2, server, path_result, server_result,
        )


class TestTemplateConcretePaths(
        BaseTestSpecServer, BaseTestSimpleServer):

    path_name = '/keys/{id}/tokens/{id2}'

    @pytest.fixture
    def operation_2(self):
        return Operation('get', '/keys/{id}/tokens/master', {}, {})

    @pytest.fixture
    def operations_2(self, operation_2):
        return {
            'get': operation_2,
        }

    @pytest.fixture
    def path(self, operations):
        return Path('/keys/{id}/tokens/{id2}', operations)

    @pytest.fixture
    def path_2(self, operations_2):
        return Path('/keys/{id}/tokens/master', operations_2)

    @pytest.fixture
    def paths(self, path, path_2):
        return {
            path.name: path,
            path_2.name: path_2,
        }

    def test_valid(self, finder, path_2, operation_2, server):
        token_id = '123'
        request_uri = '/keys/{0}/tokens/master'.format(token_id)
        request = MockRequest(
            'http://petstore.swagger.io', 'get', request_uri)
        result = finder.find(request)

        path_result = TemplateResult(path_2.name, {'id': '123'})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path_2, operation_2, server, path_result, server_result,
        )
