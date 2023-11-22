from pathlib import Path

import pytest

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core.exceptions import SpecError


class TestOpenAPIFromPath:
    def test_valid(self, create_file):
        spec_dict = {
            "openapi": "3.1.0",
            "info": {
                "title": "Spec",
                "version": "0.0.1",
            },
            "paths": {},
        }
        file_path = create_file(spec_dict)
        path = Path(file_path)
        result = OpenAPI.from_path(path)

        assert type(result) == OpenAPI
        assert result.spec.contents() == spec_dict


class TestOpenAPIFromFilePath:
    def test_valid(self, create_file):
        spec_dict = {
            "openapi": "3.1.0",
            "info": {
                "title": "Spec",
                "version": "0.0.1",
            },
            "paths": {},
        }
        file_path = create_file(spec_dict)
        result = OpenAPI.from_file_path(file_path)

        assert type(result) == OpenAPI
        assert result.spec.contents() == spec_dict


class TestOpenAPIFromFile:
    def test_valid(self, create_file):
        spec_dict = {
            "openapi": "3.1.0",
            "info": {
                "title": "Spec",
                "version": "0.0.1",
            },
            "paths": {},
        }
        file_path = create_file(spec_dict)
        with open(file_path) as f:
            result = OpenAPI.from_file(f)

        assert type(result) == OpenAPI
        assert result.spec.contents() == spec_dict


class TestOpenAPIFromDict:
    def test_spec_error(self):
        spec_dict = {}

        with pytest.raises(SpecError):
            OpenAPI.from_dict(spec_dict)

    def test_check_skipped(self):
        spec_dict = {}
        config = Config(spec_validator_cls=None)

        result = OpenAPI.from_dict(spec_dict, config=config)

        assert type(result) == OpenAPI
        assert result.spec.contents() == spec_dict
