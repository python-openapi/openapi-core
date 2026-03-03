from pathlib import Path

import pytest

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core import V3RequestUnmarshaller
from openapi_core import V3RequestValidator
from openapi_core import V3ResponseUnmarshaller
from openapi_core import V3ResponseValidator
from openapi_core.exceptions import SpecError
from openapi_core.unmarshalling.request import V32RequestUnmarshaller
from openapi_core.unmarshalling.request import V32WebhookRequestUnmarshaller
from openapi_core.unmarshalling.response import V32ResponseUnmarshaller
from openapi_core.unmarshalling.response import V32WebhookResponseUnmarshaller
from openapi_core.validation.request import V32RequestValidator
from openapi_core.validation.request import V32WebhookRequestValidator
from openapi_core.validation.response import V32ResponseValidator
from openapi_core.validation.response import V32WebhookResponseValidator


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
        assert result.spec.read_value() == spec_dict


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
        assert result.spec.read_value() == spec_dict


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
        assert result.spec.read_value() == spec_dict


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
        assert result.spec.read_value() == spec_dict


class TestOpenAPIVersion32:
    def test_v3_aliases_use_v32(self):
        assert V3RequestValidator is V32RequestValidator
        assert V3ResponseValidator is V32ResponseValidator
        assert V3RequestUnmarshaller is V32RequestUnmarshaller
        assert V3ResponseUnmarshaller is V32ResponseUnmarshaller

    def test_default_request_validator(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert result.request_validator_cls is V32RequestValidator

    def test_default_response_validator(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert result.response_validator_cls is V32ResponseValidator

    def test_default_request_unmarshaller(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert result.request_unmarshaller_cls is V32RequestUnmarshaller

    def test_default_response_unmarshaller(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert result.response_unmarshaller_cls is V32ResponseUnmarshaller

    def test_default_webhook_request_validator(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert (
            result.webhook_request_validator_cls is V32WebhookRequestValidator
        )

    def test_default_webhook_response_validator(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert (
            result.webhook_response_validator_cls
            is V32WebhookResponseValidator
        )

    def test_default_webhook_request_unmarshaller(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert (
            result.webhook_request_unmarshaller_cls
            is V32WebhookRequestUnmarshaller
        )

    def test_default_webhook_response_unmarshaller(self, spec_v32):
        result = OpenAPI(spec_v32)

        assert (
            result.webhook_response_unmarshaller_cls
            is V32WebhookResponseUnmarshaller
        )
