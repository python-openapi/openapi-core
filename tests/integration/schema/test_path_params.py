import pytest
from openapi_spec_validator import openapi_v30_spec_validator
from openapi_spec_validator import openapi_v31_spec_validator

from openapi_core.shortcuts import create_spec


class BaseTestMinimal:
    def test_param_present(self, factory, spec_path, spec_validator):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict, spec_validator=spec_validator)

        path = spec / "paths#/resource/{resId}"

        parameters = path / "parameters"
        assert len(parameters) == 1

        param = parameters[0]
        assert param["name"] == "resId"
        assert param["required"]
        assert param["in"] == "path"


class Test30Minimal(BaseTestMinimal):
    @pytest.fixture
    def spec_path(self, factory):
        return "data/v3.0/path_param.yaml"

    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v30_spec_validator


class Test31Minimal(BaseTestMinimal):
    @pytest.fixture
    def spec_path(self, factory):
        return "data/v3.1/path_param.yaml"

    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v31_spec_validator
