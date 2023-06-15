from os import path
from urllib import request

import pytest
from openapi_spec_validator.readers import read_from_filename
from yaml import safe_load

from openapi_core.spec import Spec


def content_from_file(spec_file):
    directory = path.abspath(path.dirname(__file__))
    path_full = path.join(directory, spec_file)
    return read_from_filename(path_full)


def spec_from_file(spec_file):
    spec_dict, base_uri = content_from_file(spec_file)
    return Spec.from_dict(spec_dict, base_uri=base_uri)


def spec_from_url(base_uri):
    content = request.urlopen(base_uri)
    spec_dict = safe_load(content)
    return Spec.from_dict(spec_dict, base_uri=base_uri)


class Factory(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


@pytest.fixture(scope="session")
def factory():
    return Factory(
        content_from_file=content_from_file,
        spec_from_file=spec_from_file,
        spec_from_url=spec_from_url,
    )


@pytest.fixture(scope="session")
def v30_petstore_content(factory):
    content, _ = factory.content_from_file("data/v3.0/petstore.yaml")
    return content


@pytest.fixture(scope="session")
def v30_petstore_spec(v30_petstore_content):
    base_uri = "file://tests/integration/data/v3.0/petstore.yaml"
    return Spec.from_dict(v30_petstore_content, base_uri=base_uri)
