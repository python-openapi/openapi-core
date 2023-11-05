from json import dumps

import pytest
import responses
from werkzeug.test import Client
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

from openapi_core import V30RequestUnmarshaller
from openapi_core import V30ResponseUnmarshaller
from openapi_core.contrib.werkzeug import WerkzeugOpenAPIRequest
from openapi_core.contrib.werkzeug import WerkzeugOpenAPIResponse


class TestWerkzeugOpenAPIValidation:
    @pytest.fixture
    def schema_path(self, schema_path_factory):
        specfile = "contrib/requests/data/v3.1/requests_factory.yaml"
        return schema_path_factory.from_file(specfile)

    @pytest.fixture
    def app(self):
        def test_app(environ, start_response):
            req = Request(environ, populate_request=False)
            if req.args.get("q") == "string":
                response = Response(
                    dumps({"data": "data"}),
                    headers={"X-Rate-Limit": "12"},
                    mimetype="application/json",
                    status=200,
                )
            else:
                response = Response("Not Found", status=404)
            return response(environ, start_response)

        return test_app

    @pytest.fixture
    def client(self, app):
        return Client(app)

    def test_request_validator_root_path(self, client, schema_path):
        query_string = {
            "q": "string",
        }
        headers = {"content-type": "application/json"}
        data = {"param1": 1}
        response = client.post(
            "/12/",
            base_url="http://localhost/browse",
            query_string=query_string,
            json=data,
            headers=headers,
        )
        openapi_request = WerkzeugOpenAPIRequest(response.request)
        unmarshaller = V30RequestUnmarshaller(schema_path)
        result = unmarshaller.unmarshal(openapi_request)
        assert not result.errors

    def test_request_validator_path_pattern(self, client, schema_path):
        query_string = {
            "q": "string",
        }
        headers = {"content-type": "application/json"}
        data = {"param1": 1}
        response = client.post(
            "/browse/12/",
            base_url="http://localhost",
            query_string=query_string,
            json=data,
            headers=headers,
        )
        openapi_request = WerkzeugOpenAPIRequest(response.request)
        unmarshaller = V30RequestUnmarshaller(schema_path)
        result = unmarshaller.unmarshal(openapi_request)
        assert not result.errors

    @responses.activate
    def test_response_validator_path_pattern(self, client, schema_path):
        query_string = {
            "q": "string",
        }
        headers = {"content-type": "application/json"}
        data = {"param1": 1}
        response = client.post(
            "/browse/12/",
            base_url="http://localhost",
            query_string=query_string,
            json=data,
            headers=headers,
        )
        openapi_request = WerkzeugOpenAPIRequest(response.request)
        openapi_response = WerkzeugOpenAPIResponse(response)
        unmarshaller = V30ResponseUnmarshaller(schema_path)
        result = unmarshaller.unmarshal(openapi_request, openapi_response)
        assert not result.errors
