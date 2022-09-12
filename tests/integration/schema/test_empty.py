import pytest
from jsonschema.exceptions import ValidationError

from openapi_core.spec import Spec


class TestEmpty:
    def test_raises_on_invalid(self):
        with pytest.raises(ValidationError):
            Spec.create("")
