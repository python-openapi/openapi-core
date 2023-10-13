import pytest
from jsonschema_path import SchemaPath


@pytest.fixture
def spec_v20():
    return SchemaPath.from_dict({"swagger": "2.0"})


@pytest.fixture
def spec_v30():
    return SchemaPath.from_dict({"openapi": "3.0.0"})


@pytest.fixture
def spec_v31():
    return SchemaPath.from_dict(
        {
            "openapi": "3.1.0",
            "info": {
                "title": "Spec",
                "version": "0.0.1",
            },
            "paths": {},
        }
    )


@pytest.fixture
def spec_invalid():
    return SchemaPath.from_dict({})
