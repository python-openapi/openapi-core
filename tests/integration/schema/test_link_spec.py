import pytest


class TestLinkSpec:
    @pytest.mark.parametrize(
        "spec_file",
        [
            "data/v3.0/links.yaml",
            "data/v3.1/links.yaml",
        ],
    )
    def test_no_param(self, spec_file, schema_path_factory):
        schema_path = schema_path_factory.from_file(spec_file)
        resp = schema_path / "paths#/status#get#responses#default"

        links = resp / "links"
        assert len(links) == 1

        link = links / "noParamLink"
        assert link["operationId"] == "noParOp"
        assert "server" not in link
        assert "requestBody" not in link
        assert "parameters" not in link

    @pytest.mark.parametrize(
        "spec_file",
        [
            "data/v3.0/links.yaml",
            "data/v3.1/links.yaml",
        ],
    )
    def test_param(self, spec_file, schema_path_factory):
        schema_path = schema_path_factory.from_file(spec_file)
        resp = schema_path / "paths#/status/{resourceId}#get#responses#default"

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
