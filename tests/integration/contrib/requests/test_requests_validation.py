import pytest
import requests
import responses

from openapi_core import V31RequestValidator
from openapi_core import V31ResponseValidator
from openapi_core import V31WebhookRequestValidator
from openapi_core import V31WebhookResponseValidator
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.contrib.requests import RequestsOpenAPIResponse
from openapi_core.contrib.requests import RequestsOpenAPIWebhookRequest


class TestRequestsOpenAPIValidation:
    @pytest.fixture
    def spec(self, factory):
        specfile = "contrib/requests/data/v3.0/requests_factory.yaml"
        return factory.spec_from_file(specfile)

    @pytest.fixture
    def request_validator(self, spec):
        return V31RequestValidator(spec)

    @pytest.fixture
    def response_validator(self, spec):
        return V31ResponseValidator(spec)

    @pytest.fixture
    def webhook_request_validator(self, spec):
        return V31WebhookRequestValidator(spec)

    @pytest.fixture
    def webhook_response_validator(self, spec):
        return V31WebhookResponseValidator(spec)

    @responses.activate
    def test_response_validator_path_pattern(self, response_validator):
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
        result = response_validator.validate(openapi_request, openapi_response)
        assert not result.errors

    def test_request_validator_path_pattern(self, request_validator):
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        openapi_request = RequestsOpenAPIRequest(request)
        result = request_validator.validate(openapi_request)
        assert not result.errors

    def test_request_validator_prepared_request(self, request_validator):
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        request_prepared = request.prepare()
        openapi_request = RequestsOpenAPIRequest(request_prepared)
        result = request_validator.validate(openapi_request)
        assert not result.errors

    def test_webhook_request_validator_path(self, webhook_request_validator):
        request = requests.Request(
            "POST",
            "http://otherhost/callback/",
            headers={
                "content-type": "application/json",
                "X-Rate-Limit": "12",
            },
            json={"id": 1},
        )
        openapi_webhook_request = RequestsOpenAPIWebhookRequest(
            request, "resourceAdded"
        )
        result = webhook_request_validator.validate(openapi_webhook_request)
        assert not result.errors

    @responses.activate
    def test_webhook_response_validator_path(self, webhook_response_validator):
        responses.add(
            responses.POST,
            "http://otherhost/callback/",
            json={"data": "data"},
            status=200,
        )
        request = requests.Request(
            "POST",
            "http://otherhost/callback/",
            headers={
                "content-type": "application/json",
                "X-Rate-Limit": "12",
            },
            json={"id": 1},
        )
        request_prepared = request.prepare()
        session = requests.Session()
        response = session.send(request_prepared)
        openapi_webhook_request = RequestsOpenAPIWebhookRequest(
            request, "resourceAdded"
        )
        openapi_response = RequestsOpenAPIResponse(response)
        result = webhook_response_validator.validate(
            openapi_webhook_request, openapi_response
        )
        assert not result.errors
