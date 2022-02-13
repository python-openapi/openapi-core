import pytest

from openapi_core.spec import OpenAPIv30Spec as Spec


class TestMinimal:

    spec_paths = ["data/v3.0/path_param.yaml"]

    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_param_present(self, factory, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = Spec.create(spec_dict)

        path = spec / "paths#/resource/{resId}"

        parameters = path / "parameters"
        assert len(parameters) == 1

        param = parameters[0]
        assert param["name"] == "resId"
        assert param["required"]
        assert param["in"] == "path"
