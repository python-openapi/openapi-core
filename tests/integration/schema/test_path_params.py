import pytest


class TestMinimal:
    @pytest.mark.parametrize(
        "spec_file",
        [
            "data/v3.0/path_param.yaml",
            "data/v3.1/path_param.yaml",
        ],
    )
    def test_param_present(self, spec_file, schema_path_factory):
        schema_path = schema_path_factory.from_file(spec_file)

        path = schema_path / "paths#/resource/{resId}"

        parameters = path / "parameters"
        assert len(parameters) == 1

        param = parameters[0]
        assert param["name"] == "resId"
        assert param["required"]
        assert param["in"] == "path"
