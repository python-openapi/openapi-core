import pytest
from jsonschema_path import SchemaPath


@pytest.fixture
def spec_v30():
    return SchemaPath.from_dict({"openapi": "3.0"})


@pytest.fixture
def spec_v31():
    return SchemaPath.from_dict({"openapi": "3.1"})


@pytest.fixture
def spec_invalid():
    return SchemaPath.from_dict({})
