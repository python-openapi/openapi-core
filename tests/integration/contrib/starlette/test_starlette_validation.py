from json import dumps

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from openapi_core import unmarshal_request
from openapi_core import unmarshal_response
from openapi_core.contrib.starlette import StarletteOpenAPIRequest
from openapi_core.contrib.starlette import StarletteOpenAPIResponse


class TestV30StarletteFactory:
    @pytest.fixture
    def schema_path(self, schema_path_factory):
        specfile = "contrib/starlette/data/v3.0/starlette_factory.yaml"
        return schema_path_factory.from_file(specfile)

    @pytest.fixture
    def app(self):
        async def test_route(scope, receive, send):
            request = Request(scope, receive)
            if request.args.get("q") == "string":
                response = JSONResponse(
                    dumps({"data": "data"}),
                    headers={"X-Rate-Limit": "12"},
                    mimetype="application/json",
                    status=200,
                )
            else:
                response = PlainTextResponse("Not Found", status=404)
            await response(scope, receive, send)

        return Starlette(
            routes=[
                Route("/browse/12/", test_route),
            ],
        )

    @pytest.fixture
    def client(self, app):
        return TestClient(app, base_url="http://localhost")

    def test_request_validator_path_pattern(self, client, schema_path):
        response_data = {"data": "data"}

        async def test_route(request):
            body = await request.body()
            openapi_request = StarletteOpenAPIRequest(request, body)
            result = unmarshal_request(openapi_request, schema_path)
            assert not result.errors
            return JSONResponse(
                response_data,
                headers={"X-Rate-Limit": "12"},
                media_type="application/json",
                status_code=200,
            )

        app = Starlette(
            routes=[
                Route("/browse/12/", test_route, methods=["POST"]),
            ],
        )
        client = TestClient(app, base_url="http://localhost")
        query_string = {
            "q": "string",
        }
        headers = {"content-type": "application/json"}
        data = {"param1": 1}
        response = client.post(
            "/browse/12/",
            params=query_string,
            json=data,
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json() == response_data

    def test_response_validator_path_pattern(self, client, schema_path):
        response_data = {"data": "data"}

        def test_route(request):
            response = JSONResponse(
                response_data,
                headers={"X-Rate-Limit": "12"},
                media_type="application/json",
                status_code=200,
            )
            openapi_request = StarletteOpenAPIRequest(request)
            openapi_response = StarletteOpenAPIResponse(response)
            result = unmarshal_response(
                openapi_request, openapi_response, schema_path
            )
            assert not result.errors
            return response

        app = Starlette(
            routes=[
                Route("/browse/12/", test_route, methods=["POST"]),
            ],
        )
        client = TestClient(app, base_url="http://localhost")
        query_string = {
            "q": "string",
        }
        headers = {"content-type": "application/json"}
        data = {"param1": 1}
        response = client.post(
            "/browse/12/",
            params=query_string,
            json=data,
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json() == response_data
