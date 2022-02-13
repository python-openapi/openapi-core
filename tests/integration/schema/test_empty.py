import pytest
from jsonschema.exceptions import ValidationError

from openapi_core.spec import OpenAPIv30Spec as Spec


class TestEmpty:
    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/empty.yaml")

    @pytest.fixture
    def spec(self, spec_dict):
        return Spec.create(spec_dict)

    def test_raises_on_invalid(self, spec_dict):
        with pytest.raises(ValidationError):
            Spec.create(spec_dict)
