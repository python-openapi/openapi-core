from json import dumps
from pathlib import Path
from typing import Any
from typing import cast

import pytest
import yaml
from falcon import status_codes
from falcon.asgi import App
from falcon.asgi import Response
from falcon.constants import MEDIA_JSON
from falcon.testing import ASGIConductor
from jsonschema_path import SchemaPath

from openapi_core.contrib.falcon.middlewares import FalconASGIOpenAPIMiddleware
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware
from openapi_core.contrib.falcon.requests import FalconAsgiOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconAsgiOpenAPIResponse
from openapi_core.contrib.falcon.util import serialize_body


@pytest.fixture
def spec():
    openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
    spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
    return SchemaPath.from_dict(spec_dict)


class PetListResource:
    async def on_get(self, req, resp):
        assert req.context.openapi
        assert not req.context.openapi.errors
        resp.status = status_codes.HTTP_200
        resp.content_type = MEDIA_JSON
        resp.text = dumps(
            {
                "data": [
                    {
                        "id": 12,
                        "name": "Cat",
                        "ears": {
                            "healthy": True,
                        },
                    }
                ]
            }
        )
        resp.set_header("X-Rate-Limit", "12")


class InvalidPetListResource:
    async def on_get(self, req, resp):
        assert req.context.openapi
        assert not req.context.openapi.errors
        resp.status = status_codes.HTTP_200
        resp.content_type = MEDIA_JSON
        resp.text = dumps({"data": [{"id": "12", "name": 13}]})
        resp.set_header("X-Rate-Limit", "12")


class _AsyncStream:
    def __init__(self, chunks):
        self._chunks = chunks
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._chunks):
            raise StopAsyncIteration

        chunk = self._chunks[self._index]
        self._index += 1
        return chunk


@pytest.mark.asyncio
async def test_dual_mode_sync_middleware_works_with_asgi_app(spec):
    middleware = FalconOpenAPIMiddleware.from_spec(spec)
    app = App(middleware=[middleware])
    app.add_route("/v1/pets", PetListResource())

    async with ASGIConductor(app) as conductor:
        with pytest.warns(DeprecationWarning):
            response = await conductor.simulate_get(
                "/v1/pets",
                host="petstore.swagger.io",
                query_string="limit=12",
            )

    assert response.status_code == 200
    assert response.json == {
        "data": [
            {
                "id": 12,
                "name": "Cat",
                "ears": {
                    "healthy": True,
                },
            }
        ]
    }


@pytest.mark.asyncio
async def test_explicit_asgi_middleware_handles_request_validation(spec):
    middleware = FalconASGIOpenAPIMiddleware.from_spec(spec)
    app = App(middleware=[middleware])
    app.add_route("/v1/pets", PetListResource())

    async with ASGIConductor(app) as conductor:
        with pytest.warns(DeprecationWarning):
            response = await conductor.simulate_get(
                "/v1/pets",
                host="petstore.swagger.io",
            )

    assert response.status_code == 400
    assert response.json == {
        "errors": [
            {
                "type": (
                    "<class 'openapi_core.validation.request.exceptions."
                    "MissingRequiredParameter'>"
                ),
                "status": 400,
                "title": "Missing required query parameter: limit",
            }
        ]
    }


@pytest.mark.asyncio
async def test_explicit_asgi_middleware_validates_response(spec):
    middleware = FalconASGIOpenAPIMiddleware.from_spec(spec)
    app = App(middleware=[middleware])
    app.add_route("/v1/pets", InvalidPetListResource())

    async with ASGIConductor(app) as conductor:
        with pytest.warns(DeprecationWarning):
            response = await conductor.simulate_get(
                "/v1/pets",
                host="petstore.swagger.io",
                query_string="limit=12",
            )

    assert response.status_code == 400
    assert "errors" in response.json


@pytest.mark.asyncio
async def test_asgi_response_adapter_handles_stream_without_charset():
    chunks = [
        b'{"data": [',
        b'{"id": 12, "name": "Cat", "ears": {"healthy": true}}',
        b"]}",
    ]
    response = Response()
    response.content_type = MEDIA_JSON
    response.stream = _AsyncStream(chunks)

    openapi_response = await FalconAsgiOpenAPIResponse.from_response(response)

    assert openapi_response.data == b"".join(chunks)
    assert response.stream is not None

    replayed_chunks = []
    async for chunk in response.stream:
        replayed_chunks.append(chunk)
    assert b"".join(replayed_chunks) == b"".join(chunks)


def test_asgi_request_body_cached_none_skips_media_deserialization():
    class _DummyRequest:
        def get_media(self, *args, **kwargs):
            raise AssertionError("get_media should not be called")

    openapi_request = object.__new__(FalconAsgiOpenAPIRequest)
    openapi_request.request = cast(Any, _DummyRequest())
    openapi_request._body = None

    assert openapi_request.body is None


def test_multipart_unsupported_serialization_warns_and_returns_none():
    content_type = "multipart/form-data; boundary=test"

    class _DummyHandler:
        def serialize(self, media, content_type):
            raise NotImplementedError(
                "multipart form serialization unsupported"
            )

    class _DummyMediaHandlers:
        def _resolve(self, content_type, default_media_type):
            return (_DummyHandler(), content_type, None)

    class _DummyOptions:
        media_handlers = _DummyMediaHandlers()
        default_media_type = MEDIA_JSON

    class _DummyRequest:
        options = _DummyOptions()

    with pytest.warns(
        UserWarning,
        match="body serialization for multipart/form-data",
    ):
        body = serialize_body(
            cast(Any, _DummyRequest()), {"name": "Cat"}, content_type
        )

    assert body is None
