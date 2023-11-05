from json import dumps
from os import unlink
from tempfile import NamedTemporaryFile

import pytest
from jsonschema_path import SchemaPath


@pytest.fixture
def spec_v20():
    return SchemaPath.from_dict(
        {
            "swagger": "2.0",
            "info": {
                "title": "Spec",
                "version": "0.0.1",
            },
            "paths": {},
        }
    )


@pytest.fixture
def spec_v30():
    return SchemaPath.from_dict(
        {
            "openapi": "3.0.0",
            "info": {
                "title": "Spec",
                "version": "0.0.1",
            },
            "paths": {},
        }
    )


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


@pytest.fixture
def create_file():
    files = []

    def create(schema):
        contents = dumps(schema).encode("utf-8")
        with NamedTemporaryFile(delete=False) as tf:
            files.append(tf)
            tf.write(contents)
        return tf.name

    yield create
    for tf in files:
        unlink(tf.name)
