import pytest
from jsonschema_path import SchemaPath

from openapi_core.templating.datatypes import TemplateResult
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import PathsNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.paths.finders import APICallPathFinder


class BaseTestSimpleServer:
    server_url = "http://petstore.swagger.io"

    @pytest.fixture
    def server_variable(self):
        return {}

    @pytest.fixture
    def server_variables(self, server_variable):
        if not server_variable:
            return {}
        return {
            self.server_variable_name: server_variable,
        }

    @pytest.fixture
    def server(self, server_variables):
        server = {
            "url": self.server_url,
        }
        if server_variables:
            server["variables"] = server_variables
        return server

    @pytest.fixture
    def servers(self, server):
        return [
            server,
        ]


class BaseTestVariableServer(BaseTestSimpleServer):
    server_url = "http://petstore.swagger.io/{version}"
    server_variable_name = "version"
    server_variable_default = "v1"
    server_variable_enum = ["v1", "v2"]

    @pytest.fixture
    def server_variable(self):
        return {
            self.server_variable_name: {
                "default": self.server_variable_default,
                "enum": self.server_variable_enum,
            }
        }


class BaseTestSimplePath:
    path_name = "/resource"

    @pytest.fixture
    def path(self, operations):
        return operations

    @pytest.fixture
    def paths(self, path):
        return {
            self.path_name: path,
        }


class BaseTestVariablePath(BaseTestSimplePath):
    path_name = "/resource/{resource_id}"
    path_parameter_name = "resource_id"

    @pytest.fixture
    def parameter(self):
        return {
            "name": self.path_parameter_name,
            "in": "path",
        }

    @pytest.fixture
    def parameters(self, parameter):
        return [
            parameter,
        ]

    @pytest.fixture
    def path(self, operations, parameters):
        path = operations.copy()
        path["parameters"] = parameters
        return path


class BaseTestSpecServer:
    location = "spec"

    @pytest.fixture
    def info(self):
        return {
            "title": "Test schema",
            "version": "1.0",
        }

    @pytest.fixture
    def operation(self):
        return {
            "responses": [],
        }

    @pytest.fixture
    def operations(self, operation):
        return {
            "get": operation,
        }

    @pytest.fixture
    def spec(self, info, paths, servers):
        spec = {
            "info": info,
            "servers": servers,
            "paths": paths,
        }
        return SchemaPath.from_dict(spec)

    @pytest.fixture
    def finder(self, spec):
        return APICallPathFinder(spec)


class BaseTestPathServer(BaseTestSpecServer):
    location = "path"

    @pytest.fixture
    def path(self, operations, servers):
        path = operations.copy()
        path["servers"] = servers
        return path

    @pytest.fixture
    def spec(self, info, paths):
        spec = {
            "info": info,
            "paths": paths,
        }
        return SchemaPath.from_dict(spec)


class BaseTestOperationServer(BaseTestSpecServer):
    location = "operation"

    @pytest.fixture
    def operation(self, servers):
        return {
            "responses": [],
            "servers": servers,
        }

    @pytest.fixture
    def spec(self, info, paths):
        spec = {
            "info": info,
            "paths": paths,
        }
        return SchemaPath.from_dict(spec)


class BaseTestServerNotFound:
    @pytest.fixture
    def servers(self):
        return [
            SchemaPath.from_dict(
                {"url": "http://petstore.swagger.io/resource"}
            )
        ]

    def test_raises(self, finder):
        method = "get"
        full_url = "http://invalidserver/resource"

        with pytest.raises(ServerNotFound):
            finder.find(method, full_url)


class BaseTestDefaultServer:
    @pytest.fixture
    def servers(self):
        return []

    def test_returns_default_server(self, finder, spec):
        method = "get"
        full_url = "http://petstore.swagger.io/resource"

        result = finder.find(method, full_url)

        path = spec / "paths" / self.path_name
        operation = spec / "paths" / self.path_name / method
        server = SchemaPath.from_dict({"url": "/"})
        path_result = TemplateResult(self.path_name, {})
        server_result = TemplateResult("/", {})
        assert result == (
            path,
            operation,
            server,
            path_result,
            server_result,
        )


class BaseTestOperationNotFound:
    @pytest.fixture
    def operations(self):
        return {}

    def test_raises(self, finder):
        method = "get"
        full_url = "http://petstore.swagger.io/resource"

        with pytest.raises(OperationNotFound):
            finder.find(method, full_url)


class BaseTestValid:
    def test_simple(self, finder, spec):
        method = "get"
        full_url = "http://petstore.swagger.io/resource"

        result = finder.find(method, full_url)

        path = spec / "paths" / self.path_name
        operation = spec / "paths" / self.path_name / method
        server = eval(self.location) / "servers" / 0
        path_result = TemplateResult(self.path_name, {})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path,
            operation,
            server,
            path_result,
            server_result,
        )


class BaseTestVariableValid:
    @pytest.mark.parametrize("version", ["v1", "v2", ""])
    def test_variable(self, finder, spec, version):
        method = "get"
        full_url = f"http://petstore.swagger.io/{version}/resource"

        result = finder.find(method, full_url)

        path = spec / "paths" / self.path_name
        operation = spec / "paths" / self.path_name / method
        server = eval(self.location) / "servers" / 0
        path_result = TemplateResult(self.path_name, {})
        server_result = TemplateResult(self.server_url, {"version": version})
        assert result == (
            path,
            operation,
            server,
            path_result,
            server_result,
        )


class BaseTestPathVariableValid:
    @pytest.mark.parametrize("res_id", ["111", "222"])
    def test_path_variable(self, finder, spec, res_id):
        method = "get"
        full_url = f"http://petstore.swagger.io/resource/{res_id}"

        result = finder.find(method, full_url)

        path = spec / "paths" / self.path_name
        operation = spec / "paths" / self.path_name / method
        server = eval(self.location) / "servers" / 0
        path_result = TemplateResult(self.path_name, {"resource_id": res_id})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path,
            operation,
            server,
            path_result,
            server_result,
        )


class BaseTestPathNotFound:
    @pytest.fixture
    def paths(self):
        return {}

    def test_raises(self, finder):
        method = "get"
        full_url = "http://petstore.swagger.io/resource"

        with pytest.raises(PathNotFound):
            finder.find(method, full_url)


class BaseTestPathsNotFound:
    @pytest.fixture
    def spec(self, info):
        spec = {
            "info": info,
        }
        return SchemaPath.from_dict(spec)

    def test_raises(self, finder):
        method = "get"
        full_url = "http://petstore.swagger.io/resource"

        with pytest.raises(PathsNotFound):
            finder.find(method, full_url)


class TestSpecSimpleServerDefaultServer(
    BaseTestDefaultServer,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestSpecSimpleServerServerNotFound(
    BaseTestServerNotFound,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestSpecSimpleServerOperationNotFound(
    BaseTestOperationNotFound,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestSpecSimpleServerPathNotFound(
    BaseTestPathNotFound,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestSpecSimpleServerPathsNotFound(
    BaseTestPathsNotFound,
    BaseTestSpecServer,
    BaseTestSimpleServer,
):
    pass


class TestOperationSimpleServerDefaultServer(
    BaseTestDefaultServer,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestOperationSimpleServerServerNotFound(
    BaseTestServerNotFound,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestOperationSimpleServerOperationNotFound(
    BaseTestOperationNotFound,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestOperationSimpleServerPathNotFound(
    BaseTestPathNotFound,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestOperationSimpleServerPathsNotFound(
    BaseTestPathsNotFound,
    BaseTestOperationServer,
    BaseTestSimpleServer,
):
    pass


class TestPathSimpleServerDefaultServer(
    BaseTestDefaultServer,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestPathSimpleServerServerNotFound(
    BaseTestServerNotFound,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestPathSimpleServerOperationNotFound(
    BaseTestOperationNotFound,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestPathSimpleServerPathNotFound(
    BaseTestPathNotFound,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestPathSimpleServerPathsNotFound(
    BaseTestPathsNotFound,
    BaseTestPathServer,
    BaseTestSimpleServer,
):
    pass


class TestSpecSimpleServerValid(
    BaseTestValid, BaseTestSpecServer, BaseTestSimplePath, BaseTestSimpleServer
):
    pass


class TestOperationSimpleServerValid(
    BaseTestValid,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestSimpleServer,
):
    pass


class TestPathSimpleServerValid(
    BaseTestValid, BaseTestPathServer, BaseTestSimplePath, BaseTestSimpleServer
):
    pass


class TestSpecSimpleServerVariablePathValid(
    BaseTestPathVariableValid,
    BaseTestSpecServer,
    BaseTestVariablePath,
    BaseTestSimpleServer,
):
    pass


class TestOperationSimpleServerVariablePathValid(
    BaseTestPathVariableValid,
    BaseTestOperationServer,
    BaseTestVariablePath,
    BaseTestSimpleServer,
):
    pass


class TestPathSimpleServerVariablePathValid(
    BaseTestPathVariableValid,
    BaseTestPathServer,
    BaseTestVariablePath,
    BaseTestSimpleServer,
):
    pass


class TestSpecVariableServerDefaultServer(
    BaseTestDefaultServer,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestSpecVariableServerServerNotFound(
    BaseTestServerNotFound,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestSpecVariableServerOperationNotFound(
    BaseTestOperationNotFound,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestSpecVariableServerPathNotFound(
    BaseTestPathNotFound,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestSpecVariableServerPathsNotFound(
    BaseTestPathsNotFound,
    BaseTestSpecServer,
    BaseTestVariableServer,
):
    pass


class TestOperationVariableServerDefaultServer(
    BaseTestDefaultServer,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestOperationVariableServerServerNotFound(
    BaseTestServerNotFound,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestOperationVariableServerOperationNotFound(
    BaseTestOperationNotFound,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestOperationVariableServerPathNotFound(
    BaseTestPathNotFound,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestOperationVariableServerPathsNotFound(
    BaseTestPathsNotFound,
    BaseTestOperationServer,
    BaseTestVariableServer,
):
    pass


class TestPathVariableServerDefaultServer(
    BaseTestDefaultServer,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestPathVariableServerServerNotFound(
    BaseTestServerNotFound,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestPathVariableServerOperationNotFound(
    BaseTestOperationNotFound,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestPathVariableServerPathNotFound(
    BaseTestPathNotFound,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestPathVariableServerPathsNotFound(
    BaseTestPathsNotFound,
    BaseTestPathServer,
    BaseTestVariableServer,
):
    pass


class TestSpecVariableServerValid(
    BaseTestVariableValid,
    BaseTestSpecServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestOperationVariableServerValid(
    BaseTestVariableValid,
    BaseTestOperationServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestPathVariableServerValid(
    BaseTestVariableValid,
    BaseTestPathServer,
    BaseTestSimplePath,
    BaseTestVariableServer,
):
    pass


class TestSimilarPaths(BaseTestSpecServer, BaseTestSimpleServer):
    path_name = "/tokens"
    path_2_name = "/keys/{id}/tokens"

    @pytest.fixture
    def operation_2(self):
        return {
            "responses": [],
        }

    @pytest.fixture
    def operations_2(self, operation_2):
        return {
            "get": operation_2,
        }

    @pytest.fixture
    def path(self, operations):
        return operations

    @pytest.fixture
    def path_2(self, operations_2):
        return operations_2

    @pytest.fixture
    def paths(self, path, path_2):
        return {
            self.path_name: path,
            self.path_2_name: path_2,
        }

    def test_valid(self, finder, spec):
        token_id = "123"
        method = "get"
        full_url = f"http://petstore.swagger.io/keys/{token_id}/tokens"

        result = finder.find(method, full_url)

        path_2 = spec / "paths" / self.path_2_name
        operation_2 = spec / "paths" / self.path_2_name / method
        server = eval(self.location) / "servers" / 0
        path_result = TemplateResult(self.path_2_name, {"id": token_id})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path_2,
            operation_2,
            server,
            path_result,
            server_result,
        )


class TestConcretePaths(BaseTestSpecServer, BaseTestSimpleServer):
    path_name = "/keys/{id}/tokens"
    path_2_name = "/keys/master/tokens"

    @pytest.fixture
    def operation_2(self):
        return {
            "responses": [],
        }

    @pytest.fixture
    def operations_2(self, operation_2):
        return {
            "get": operation_2,
        }

    @pytest.fixture
    def path(self, operations):
        return operations

    @pytest.fixture
    def path_2(self, operations_2):
        return operations_2

    @pytest.fixture
    def paths(self, path, path_2):
        return {
            self.path_name: path,
            self.path_2_name: path_2,
        }

    def test_valid(self, finder, spec):
        method = "get"
        full_url = "http://petstore.swagger.io/keys/master/tokens"
        result = finder.find(method, full_url)

        path_2 = spec / "paths" / self.path_2_name
        operation_2 = spec / "paths" / self.path_2_name / method
        server = eval(self.location) / "servers" / 0
        path_result = TemplateResult(self.path_2_name, {})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path_2,
            operation_2,
            server,
            path_result,
            server_result,
        )


class TestTemplateConcretePaths(BaseTestSpecServer, BaseTestSimpleServer):
    path_name = "/keys/{id}/tokens/{id2}"
    path_2_name = "/keys/{id}/tokens/master"

    @pytest.fixture
    def operation_2(self):
        return {
            "responses": [],
        }

    @pytest.fixture
    def operations_2(self, operation_2):
        return {
            "get": operation_2,
        }

    @pytest.fixture
    def path(self, operations):
        return operations

    @pytest.fixture
    def path_2(self, operations_2):
        return operations_2

    @pytest.fixture
    def paths(self, path, path_2):
        return {
            self.path_name: path,
            self.path_2_name: path_2,
        }

    def test_valid(self, finder, spec):
        token_id = "123"
        method = "get"
        full_url = f"http://petstore.swagger.io/keys/{token_id}/tokens/master"
        result = finder.find(method, full_url)

        path_2 = spec / "paths" / self.path_2_name
        operation_2 = spec / "paths" / self.path_2_name / method
        server = eval(self.location) / "servers" / 0
        path_result = TemplateResult(self.path_2_name, {"id": "123"})
        server_result = TemplateResult(self.server_url, {})
        assert result == (
            path_2,
            operation_2,
            server,
            path_result,
            server_result,
        )
