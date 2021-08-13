import pytest
import requests
import responses
from openapi_spec_validator import openapi_v30_spec_validator

from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.contrib.requests import RequestsOpenAPIResponse
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestRequestsOpenAPIValidation:
    @pytest.fixture
    def spec(self, factory):
        specfile = "contrib/requests/data/v3.0/requests_factory.yaml"
        return create_spec(
            factory.spec_from_file(specfile),
            spec_validator=openapi_v30_spec_validator,
        )

    @responses.activate
    def test_response_validator_path_pattern(self, spec):
        responses.add(
            responses.POST,
            "http://localhost/browse/12/?q=string",
            json={"data": "data"},
            status=200,
            match_querystring=True,
            headers={"X-Rate-Limit": "12"},
        )
        validator = ResponseValidator(spec)
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        request_prepared = request.prepare()
        session = requests.Session()
        response = session.send(request_prepared)
        openapi_request = RequestsOpenAPIRequest(request)
        openapi_response = RequestsOpenAPIResponse(response)
        result = validator.validate(openapi_request, openapi_response)
        assert not result.errors

    def test_request_validator_path_pattern(self, spec):
        validator = RequestValidator(spec)
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        openapi_request = RequestsOpenAPIRequest(request)
        result = validator.validate(openapi_request)
        assert not result.errors

    def test_request_validator_prepared_request(self, spec):
        validator = RequestValidator(spec)
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        request_prepared = request.prepare()
        openapi_request = RequestsOpenAPIRequest(request_prepared)
        result = validator.validate(openapi_request)
        assert not result.errors
