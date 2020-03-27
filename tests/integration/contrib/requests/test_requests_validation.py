import pytest
import requests
import responses

from openapi_core.contrib.requests import (
    RequestsOpenAPIRequest, RequestsOpenAPIResponse,
)
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestFlaskOpenAPIValidation(object):

    @pytest.fixture
    def spec(self, factory):
        specfile = 'contrib/requests/data/v3.0/requests_factory.yaml'
        return create_spec(factory.spec_from_file(specfile))

    @responses.activate
    def test_response_validator_path_pattern(self, spec):
        responses.add(
            responses.GET, 'http://localhost/browse/12/',
            json={"data": "data"}, status=200)
        validator = ResponseValidator(spec)
        request = requests.Request('GET', 'http://localhost/browse/12/')
        request_prepared = request.prepare()
        session = requests.Session()
        response = session.send(request_prepared)
        openapi_request = RequestsOpenAPIRequest(request)
        openapi_response = RequestsOpenAPIResponse(response)
        result = validator.validate(openapi_request, openapi_response)
        assert not result.errors

    @responses.activate
    def test_request_validator_path_pattern(self, spec):
        validator = RequestValidator(spec)
        request = requests.Request('GET', 'http://localhost/browse/12/')
        openapi_request = RequestsOpenAPIRequest(request)
        result = validator.validate(openapi_request)
        assert not result.errors
