from base64 import b64decode
from os import path
from urllib import request

import pytest
from jsonschema_path import SchemaPath
from openapi_spec_validator.readers import read_from_filename
from yaml import safe_load

from openapi_core import Spec


def content_from_file(spec_file):
    directory = path.abspath(path.dirname(__file__))
    path_full = path.join(directory, spec_file)
    return read_from_filename(path_full)


def schema_path_from_file(spec_file):
    spec_dict, base_uri = content_from_file(spec_file)
    return SchemaPath.from_dict(spec_dict, base_uri=base_uri)


def schema_path_from_url(base_uri):
    content = request.urlopen(base_uri)
    spec_dict = safe_load(content)
    return SchemaPath.from_dict(spec_dict, base_uri=base_uri)


def spec_from_file(spec_file):
    schema_path = schema_path_from_file(spec_file)
    return Spec(schema_path)


def spec_from_url(base_uri):
    schema_path = schema_path_from_url(base_uri)
    return Spec(schema_path)


@pytest.fixture(scope="session")
def data_gif():
    return b64decode(
        """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
    )


class Factory(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


@pytest.fixture(scope="session")
def content_factory():
    return Factory(
        from_file=content_from_file,
    )


@pytest.fixture(scope="session")
def schema_path_factory():
    return Factory(
        from_file=schema_path_from_file,
        from_url=schema_path_from_url,
    )


@pytest.fixture(scope="session")
def spec_factory(schema_path_factory):
    return Factory(
        from_file=spec_from_file,
        from_url=spec_from_url,
    )


@pytest.fixture(scope="session")
def v30_petstore_content(content_factory):
    content, _ = content_factory.from_file("data/v3.0/petstore.yaml")
    return content


@pytest.fixture(scope="session")
def v30_petstore_spec(v30_petstore_content):
    base_uri = "file://tests/integration/data/v3.0/petstore.yaml"
    return SchemaPath.from_dict(v30_petstore_content, base_uri=base_uri)
