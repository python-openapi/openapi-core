import pytest
from openapi_spec_validator import openapi_v30_spec_validator
from openapi_spec_validator import openapi_v31_spec_validator

from openapi_core.shortcuts import create_spec
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.testing import MockRequest
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.validators import RequestValidator


class BaseTestMinimal:

    servers = [
        "http://minimal.test/",
        "https://bad.remote.domain.net/",
        "http://localhost",
        "http://localhost:8080",
        "https://u:p@a.b:1337",
    ]

    @pytest.mark.parametrize("server", servers)
    def test_hosts(self, factory, server, spec_path, spec_validator):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict, spec_validator=spec_validator)
        validator = RequestValidator(spec)
        request = MockRequest(server, "get", "/status")

        result = validator.validate(request)

        assert not result.errors

    @pytest.mark.parametrize("server", servers)
    def test_invalid_operation(
        self, factory, server, spec_path, spec_validator
    ):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict, spec_validator=spec_validator)
        validator = RequestValidator(spec)
        request = MockRequest(server, "post", "/status")

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], OperationNotFound)
        assert result.body is None
        assert result.parameters == Parameters()

    @pytest.mark.parametrize("server", servers)
    def test_invalid_path(self, factory, server, spec_path, spec_validator):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict, spec_validator=spec_validator)
        validator = RequestValidator(spec)
        request = MockRequest(server, "get", "/nonexistent")

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], PathNotFound)
        assert result.body is None
        assert result.parameters == Parameters()


class Test30Minimal(BaseTestMinimal):
    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v30_spec_validator

    @pytest.fixture
    def spec_path(self, factory):
        return "data/v3.0/minimal.yaml"


class Test30MinimalWithServers(BaseTestMinimal):
    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v30_spec_validator

    @pytest.fixture
    def spec_path(self, factory):
        return "data/v3.0/minimal_with_servers.yaml"


class Test31Minimal(BaseTestMinimal):
    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v31_spec_validator

    @pytest.fixture
    def spec_path(self, factory):
        return "data/v3.1/minimal.yaml"


class Test31MinimalWithServers(BaseTestMinimal):
    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v31_spec_validator

    @pytest.fixture
    def spec_path(self, factory):
        return "data/v3.1/minimal_with_servers.yaml"
