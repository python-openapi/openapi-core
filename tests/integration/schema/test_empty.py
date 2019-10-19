import pytest
from jsonschema.exceptions import ValidationError

from openapi_core.shortcuts import create_spec


class TestEmpty(object):

    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/empty.yaml")

    @pytest.fixture
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    def test_raises_on_invalid(self, spec_dict):
        with pytest.raises(ValidationError):
            create_spec(spec_dict)
