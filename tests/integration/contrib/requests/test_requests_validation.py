from base64 import b64encode

import pytest
import requests
import responses

from openapi_core import V30RequestUnmarshaller
from openapi_core import V30ResponseUnmarshaller
from openapi_core import V31RequestUnmarshaller
from openapi_core import V31ResponseUnmarshaller
from openapi_core import V31WebhookRequestUnmarshaller
from openapi_core import V31WebhookResponseUnmarshaller
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.contrib.requests import RequestsOpenAPIResponse
from openapi_core.contrib.requests import RequestsOpenAPIWebhookRequest


class TestV31RequestsFactory:
    @pytest.fixture
    def schema_path(self, schema_path_factory):
        specfile = "contrib/requests/data/v3.1/requests_factory.yaml"
        return schema_path_factory.from_file(specfile)

    @pytest.fixture
    def request_unmarshaller(self, schema_path):
        return V31RequestUnmarshaller(schema_path)

    @pytest.fixture
    def response_unmarshaller(self, schema_path):
        return V31ResponseUnmarshaller(schema_path)

    @pytest.fixture
    def webhook_request_unmarshaller(self, schema_path):
        return V31WebhookRequestUnmarshaller(schema_path)

    @pytest.fixture
    def webhook_response_unmarshaller(self, schema_path):
        return V31WebhookResponseUnmarshaller(schema_path)

    @responses.activate
    def test_response_validator_path_pattern(self, response_unmarshaller):
        responses.add(
            responses.POST,
            "http://localhost/browse/12/?q=string",
            json={"data": "data"},
            status=200,
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
        result = response_unmarshaller.unmarshal(
            openapi_request, openapi_response
        )
        assert not result.errors

    def test_request_validator_path_pattern(self, request_unmarshaller):
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        openapi_request = RequestsOpenAPIRequest(request)
        result = request_unmarshaller.unmarshal(openapi_request)
        assert not result.errors

    def test_request_validator_prepared_request(self, request_unmarshaller):
        request = requests.Request(
            "POST",
            "http://localhost/browse/12/",
            params={"q": "string"},
            headers={"content-type": "application/json"},
            json={"param1": 1},
        )
        request_prepared = request.prepare()
        openapi_request = RequestsOpenAPIRequest(request_prepared)
        result = request_unmarshaller.unmarshal(openapi_request)
        assert not result.errors

    def test_webhook_request_validator_path(
        self, webhook_request_unmarshaller
    ):
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
        result = webhook_request_unmarshaller.unmarshal(
            openapi_webhook_request
        )
        assert not result.errors

    @responses.activate
    def test_webhook_response_validator_path(
        self, webhook_response_unmarshaller
    ):
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
        result = webhook_response_unmarshaller.unmarshal(
            openapi_webhook_request, openapi_response
        )
        assert not result.errors


class BaseTestPetstore:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")


class TestPetstore(BaseTestPetstore):
    @pytest.fixture
    def schema_path(self, schema_path_factory):
        specfile = "data/v3.0/petstore.yaml"
        return schema_path_factory.from_file(specfile)

    @pytest.fixture
    def request_unmarshaller(self, schema_path):
        return V30RequestUnmarshaller(schema_path)

    @pytest.fixture
    def response_unmarshaller(self, schema_path):
        return V30ResponseUnmarshaller(schema_path)

    @responses.activate
    def test_response_binary_valid(self, response_unmarshaller, data_gif):
        responses.add(
            responses.GET,
            "http://petstore.swagger.io/v1/pets/1/photo",
            body=data_gif,
            content_type="image/gif",
            status=200,
        )
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
        }
        request = requests.Request(
            "GET",
            "http://petstore.swagger.io/v1/pets/1/photo",
            headers=headers,
        )
        request_prepared = request.prepare()
        session = requests.Session()
        response = session.send(request_prepared)
        openapi_request = RequestsOpenAPIRequest(request)
        openapi_response = RequestsOpenAPIResponse(response)
        result = response_unmarshaller.unmarshal(
            openapi_request, openapi_response
        )
        assert not result.errors
        assert result.data == data_gif

    @responses.activate
    def test_request_binary_valid(self, request_unmarshaller, data_gif):
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": "image/gif",
        }
        request = requests.Request(
            "POST",
            "http://petstore.swagger.io/v1/pets/1/photo",
            headers=headers,
            data=data_gif,
        )
        request_prepared = request.prepare()
        openapi_request = RequestsOpenAPIRequest(request_prepared)
        result = request_unmarshaller.unmarshal(openapi_request)
        assert not result.errors
        assert result.body == data_gif
