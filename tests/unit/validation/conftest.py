import pytest

from openapi_core import Spec


@pytest.fixture
def spec_v30():
    return Spec.from_dict({"openapi": "3.0"}, validator=None)


@pytest.fixture
def spec_v31():
    return Spec.from_dict({"openapi": "3.1"}, validator=None)


@pytest.fixture
def spec_invalid():
    return Spec.from_dict({}, validator=None)
