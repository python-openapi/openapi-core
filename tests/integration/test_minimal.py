import pytest

from openapi_core import unmarshal_request
from openapi_core import validate_request
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.testing import MockRequest


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
    def test_hosts(self, schema_path_factory, server, spec_path):
        spec = schema_path_factory.from_file(spec_path)
        request = MockRequest(server, "get", "/status")

        result = unmarshal_request(request, spec=spec)

        assert not result.errors

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_invalid_operation(self, schema_path_factory, server, spec_path):
        spec = schema_path_factory.from_file(spec_path)
        request = MockRequest(server, "post", "/status")

        with pytest.raises(OperationNotFound):
            validate_request(request, spec)

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_invalid_path(self, schema_path_factory, server, spec_path):
        spec = schema_path_factory.from_file(spec_path)
        request = MockRequest(server, "get", "/nonexistent")

        with pytest.raises(PathNotFound):
            validate_request(request, spec=spec)
