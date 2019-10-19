import pytest

from openapi_core.schema.parameters.enums import ParameterLocation
from openapi_core.shortcuts import create_spec


class TestMinimal(object):

    spec_paths = [
        "data/v3.0/path_param.yaml"
    ]

    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_param_present(self, factory, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)

        path = spec['/resource/{resId}']

        assert len(path.parameters) == 1
        param = path.parameters['resId']
        assert param.required
        assert param.location == ParameterLocation.PATH
