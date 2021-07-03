import pytest

from openapi_core.contrib.flask import FlaskOpenAPIRequest
from openapi_core.contrib.flask import FlaskOpenAPIResponse
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestFlaskOpenAPIValidation:
    @pytest.fixture
    def flask_spec(self, factory):
        specfile = "contrib/flask/data/v3.0/flask_factory.yaml"
        return create_spec(factory.spec_from_file(specfile))

    def test_response_validator_path_pattern(
        self, flask_spec, request_factory, response_factory
    ):
        validator = ResponseValidator(flask_spec)
        request = request_factory("GET", "/browse/12/", subdomain="kb")
        openapi_request = FlaskOpenAPIRequest(request)
        response = response_factory(
            '{"data": "data"}',
            status_code=200,
            headers={"X-Rate-Limit": "12"},
        )
        openapi_response = FlaskOpenAPIResponse(response)
        result = validator.validate(openapi_request, openapi_response)
        assert not result.errors

    def test_request_validator_path_pattern(self, flask_spec, request_factory):
        validator = RequestValidator(flask_spec)
        request = request_factory("GET", "/browse/12/", subdomain="kb")
        openapi_request = FlaskOpenAPIRequest(request)
        result = validator.validate(openapi_request)
        assert not result.errors
