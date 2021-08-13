import pytest
from jsonschema.exceptions import ValidationError
from openapi_spec_validator import openapi_v30_spec_validator
from openapi_spec_validator import openapi_v31_spec_validator

from openapi_core.shortcuts import create_spec


class BaseTestEmpty:
    @pytest.fixture
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    def test_raises_on_invalid(self, spec_dict, spec_validator):
        with pytest.raises(ValidationError):
            create_spec(spec_dict, spec_validator=spec_validator)


class TestEmpty30(BaseTestEmpty):
    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/empty.yaml")

    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v30_spec_validator


class TestEmpty31(BaseTestEmpty):
    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.1/empty.yaml")

    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v31_spec_validator
