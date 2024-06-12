import json
import pytest

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core.contrib.aws import APIGatewayPathFinder
from openapi_core.contrib.aws import APIGatewayAWSProxyOpenAPIRequest
from openapi_core.contrib.aws import APIGatewayAWSProxyV2OpenAPIRequest
from openapi_core.contrib.aws import APIGatewayHTTPProxyOpenAPIRequest
from openapi_core.datatypes import Parameters


class BaseTestAWSProject:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")


class TestHTTPAPI(BaseTestAWSProject):

    @pytest.fixture
    def openapi(self, content_factory):
        content, _ = content_factory.from_file("contrib/aws/data/v3.0/http-api/http_api_with_apig_ext.yaml")
        config = Config(
            path_finder_cls=APIGatewayPathFinder,
        )
        return OpenAPI.from_dict(content, config=config)

    def test_lambda_proxy_v1_event(self, openapi, content_factory):
        event, _ = content_factory.from_file("contrib/aws/data/v3.0/http-api/events/lambda-proxy.json")

        openapi_request = APIGatewayAWSProxyOpenAPIRequest(event)
        result = openapi.unmarshal_request(openapi_request)

        assert not result.errors
        assert not result.body
        assert result.parameters == Parameters(
            path={"id": "13"}
        )

    def test_lambda_proxy_v2_event(self, openapi, content_factory):
        event, _ = content_factory.from_file("contrib/aws/data/v3.0/http-api/events/lambda-proxy-v2.json")

        openapi_request = APIGatewayAWSProxyV2OpenAPIRequest(event)
        result = openapi.unmarshal_request(openapi_request)

        assert not result.errors
        assert not result.body
        assert result.parameters == Parameters(
            path={"id": "14"}
        )

    def test_http_proxy_event(self, openapi, content_factory):
        event, _ = content_factory.from_file("contrib/aws/data/v3.0/http-api/events/http-proxy.json")

        openapi_request = APIGatewayHTTPProxyOpenAPIRequest(event, base_path="/test-http-proxy")
        result = openapi.unmarshal_request(openapi_request)

        assert not result.errors
        assert not result.body
        assert result.parameters == Parameters()

    @pytest.mark.xfail(
        reason="greedy path variable to catch all requests not supported",
        strict=True,
    )
    def test_http_proxy_catch_all(self, openapi, content_factory):
        event, _ = content_factory.from_file("contrib/aws/data/v3.0/http-api/events/http-proxy-catch-all.json")

        openapi_request = APIGatewayHTTPProxyOpenAPIRequest(event, base_path="/test-http-proxy")
        result = openapi.unmarshal_request(openapi_request)

        assert not result.errors
        assert not result.body
        assert result.parameters == Parameters(
            path={"proxy": "12"}
        )
