import pytest
import requests
import responses

from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.contrib.requests import RequestsOpenAPIResponse
from openapi_core.spec import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator


class TestRequestsOpenAPIValidation:
    @pytest.fixture
    def spec(self, factory):
        specfile = "contrib/requests/data/v3.0/requests_factory.yaml"
        return Spec.create(factory.spec_from_file(specfile))

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
        result = openapi_response_validator.validate(
            spec, openapi_request, openapi_response
        )
        assert not result.errors

    def test_request_validator_path_pattern(self, spec):
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        openapi_request = RequestsOpenAPIRequest(request)
        result = openapi_request_validator.validate(spec, openapi_request)
        assert not result.errors

    def test_request_validator_prepared_request(self, spec):
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        request_prepared = request.prepare()
        openapi_request = RequestsOpenAPIRequest(request_prepared)
        result = openapi_request_validator.validate(spec, openapi_request)
        assert not result.errors
