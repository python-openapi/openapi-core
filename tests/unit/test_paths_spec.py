import pytest
from openapi_spec_validator import openapi_v31_spec_validator
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
from openapi_core import Spec


class TestSpecFromDict:
    def test_validator(self):
        schema = {}

        with pytest.warns(DeprecationWarning):
            with pytest.raises(OpenAPIValidationError):
                Spec.from_dict(schema, validator=openapi_v31_spec_validator)

    def test_validator_none(self):
        schema = {}

        with pytest.warns(DeprecationWarning):
            Spec.from_dict(schema, validator=None)

    def test_spec_validator_cls_none(self):
        schema = {}

        Spec.from_dict(schema, spec_validator_cls=None)
