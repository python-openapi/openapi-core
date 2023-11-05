import pytest

from openapi_core import Spec


class TestSpecFromDict:
    def test_deprecated(self):
        schema = {}

        with pytest.warns(DeprecationWarning):
            Spec.from_dict(schema)
