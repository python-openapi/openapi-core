import pytest
from openapi_spec_validator import openapi_v30_spec_validator
from openapi_spec_validator import openapi_v31_spec_validator

from openapi_core.shortcuts import create_spec


class BaseTestLinkSpec:
    def test_no_param(self, spec_dict, spec_validator):
        spec = create_spec(spec_dict, spec_validator=spec_validator)
        resp = spec / "paths#/status#get#responses#default"

        links = resp / "links"
        assert len(links) == 1

        link = links / "noParamLink"
        assert link["operationId"] == "noParOp"
        assert "server" not in link
        assert "requestBody" not in link
        assert "parameters" not in link

    def test_param(self, spec_dict, spec_validator):
        spec = create_spec(spec_dict, spec_validator=spec_validator)
        resp = spec / "paths#/status/{resourceId}#get#responses#default"

        links = resp / "links"
        assert len(links) == 1

        link = links / "paramLink"
        assert link["operationId"] == "paramOp"
        assert "server" not in link
        assert link["requestBody"] == "test"

        parameters = link["parameters"]
        assert len(parameters) == 1

        param = parameters["opParam"]
        assert param == "$request.path.resourceId"


class TestLinkSpec30(BaseTestLinkSpec):
    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/links.yaml")

    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v30_spec_validator


class TestLinkSpec31(BaseTestLinkSpec):
    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.1/links.yaml")

    @pytest.fixture
    def spec_validator(self, factory):
        return openapi_v31_spec_validator
