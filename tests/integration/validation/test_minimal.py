import pytest

from openapi_core import openapi_request_validator
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.testing import MockRequest
from openapi_core.validation.request.datatypes import Parameters


class TestMinimal:

    servers = [
        "http://minimal.test/",
        "https://bad.remote.domain.net/",
        "http://localhost",
        "http://localhost:8080",
        "https://u:p@a.b:1337",
    ]

    spec_paths = [
        "data/v3.0/minimal_with_servers.yaml",
        "data/v3.0/minimal.yaml",
        "data/v3.1/minimal_with_servers.yaml",
        "data/v3.1/minimal.yaml",
    ]

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_hosts(self, factory, server, spec_path):
        spec = factory.spec_from_file(spec_path)
        request = MockRequest(server, "get", "/status")

        result = openapi_request_validator.validate(spec, request)

        assert not result.errors

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_invalid_operation(self, factory, server, spec_path):
        spec = factory.spec_from_file(spec_path)
        request = MockRequest(server, "post", "/status")

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], OperationNotFound)
        assert result.body is None
        assert result.parameters == Parameters()

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_invalid_path(self, factory, server, spec_path):
        spec = factory.spec_from_file(spec_path)
        request = MockRequest(server, "get", "/nonexistent")

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], PathNotFound)
        assert result.body is None
        assert result.parameters == Parameters()
