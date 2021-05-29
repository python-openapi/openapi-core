import pytest

from openapi_core.shortcuts import create_spec
from openapi_core.templating.paths.exceptions import (
    PathNotFound, OperationNotFound,
)
from openapi_core.testing import MockRequest
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.validators import RequestValidator


class TestMinimal:

    servers = [
        "http://minimal.test/",
        "https://bad.remote.domain.net/",
        "http://localhost",
        "http://localhost:8080",
        "https://u:p@a.b:1337"
    ]

    spec_paths = [
        "data/v3.0/minimal_with_servers.yaml",
        "data/v3.0/minimal.yaml"
    ]

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_hosts(self, factory, server, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)
        validator = RequestValidator(spec)
        request = MockRequest(server, "get", "/status")

        result = validator.validate(request)

        assert not result.errors

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_invalid_operation(self, factory, server, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)
        validator = RequestValidator(spec)
        request = MockRequest(server, "post", "/status")

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], OperationNotFound)
        assert result.body is None
        assert result.parameters == Parameters()

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_invalid_path(self, factory, server, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)
        validator = RequestValidator(spec)
        request = MockRequest(server, "get", "/nonexistent")

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], PathNotFound)
        assert result.body is None
        assert result.parameters == Parameters()
