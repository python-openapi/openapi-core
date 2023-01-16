import pytest
from openapi_spec_validator.validation.exceptions import ValidatorDetectError

from openapi_core.spec import Spec


class TestEmpty:
    def test_raises_on_invalid(self):
        with pytest.raises(ValidatorDetectError):
            Spec.from_dict("")
