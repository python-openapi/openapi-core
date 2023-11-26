import asyncio
import pathlib
from typing import Any
from unittest import mock

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient

from openapi_core import V30RequestUnmarshaller
from openapi_core import V30ResponseUnmarshaller
from openapi_core.contrib.aiohttp import AIOHTTPOpenAPIWebRequest
from openapi_core.contrib.aiohttp import AIOHTTPOpenAPIWebResponse


@pytest.fixture
def schema_path(schema_path_factory):
    directory = pathlib.Path(__file__).parent
    specfile = directory / "data" / "v3.0" / "aiohttp_factory.yaml"
    return schema_path_factory.from_file(str(specfile))


@pytest.fixture
def response_getter() -> mock.MagicMock:
    # Using a mock here allows us to control the return value for different scenarios.
    return mock.MagicMock(return_value={"data": "data"})


@pytest.fixture
def no_validation(response_getter):
    async def test_route(request: web.Request) -> web.Response:
        await asyncio.sleep(0)
        response = web.json_response(
            response_getter(),
            headers={"X-Rate-Limit": "12"},
            status=200,
        )
        return response

    return test_route


@pytest.fixture
def request_validation(schema_path, response_getter):
    async def test_route(request: web.Request) -> web.Response:
        request_body = await request.text()
        openapi_request = AIOHTTPOpenAPIWebRequest(request, body=request_body)
        unmarshaller = V30RequestUnmarshaller(schema_path)
        result = unmarshaller.unmarshal(openapi_request)
        response: dict[str, Any] = response_getter()
        status = 200
        if result.errors:
            status = 400
            response = {"errors": [{"message": str(e) for e in result.errors}]}
        return web.json_response(
            response,
            headers={"X-Rate-Limit": "12"},
            status=status,
        )

    return test_route


@pytest.fixture
def response_validation(schema_path, response_getter):
    async def test_route(request: web.Request) -> web.Response:
        request_body = await request.text()
        openapi_request = AIOHTTPOpenAPIWebRequest(request, body=request_body)
        response_body = response_getter()
        response = web.json_response(
            response_body,
            headers={"X-Rate-Limit": "12"},
            status=200,
        )
        openapi_response = AIOHTTPOpenAPIWebResponse(response)
        unmarshaller = V30ResponseUnmarshaller(schema_path)
        result = unmarshaller.unmarshal(openapi_request, openapi_response)
        if result.errors:
            response = web.json_response(
                {"errors": [{"message": str(e) for e in result.errors}]},
                headers={"X-Rate-Limit": "12"},
                status=400,
            )
        return response

    return test_route


@pytest.fixture(
    params=["no_validation", "request_validation", "response_validation"]
)
def router(
    request,
    no_validation,
    request_validation,
    response_validation,
) -> web.RouteTableDef:
    test_routes = dict(
        no_validation=no_validation,
        request_validation=request_validation,
        response_validation=response_validation,
    )
    router_ = web.RouteTableDef()
    handler = test_routes[request.param]
    router_.post("/browse/{id}/")(handler)
    return router_


@pytest.fixture
def app(router):
    app = web.Application()
    app.add_routes(router)

    return app


@pytest.fixture
async def client(app, aiohttp_client) -> TestClient:
    return await aiohttp_client(app)
