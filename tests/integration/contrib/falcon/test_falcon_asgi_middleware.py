from json import dumps
from pathlib import Path

import pytest
import yaml
from falcon import status_codes
from falcon.asgi import App
from falcon.constants import MEDIA_JSON
from falcon.testing import TestClient
from jsonschema_path import SchemaPath

from openapi_core.contrib.falcon.middlewares import FalconASGIOpenAPIMiddleware
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware


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


def test_dual_mode_sync_middleware_works_with_asgi_app(spec):
    middleware = FalconOpenAPIMiddleware.from_spec(spec)
    app = App(middleware=[middleware])
    app.add_route("/v1/pets", PetListResource())
    client = TestClient(app)

    with pytest.warns(DeprecationWarning):
        response = client.simulate_get(
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


def test_explicit_asgi_middleware_handles_request_validation(spec):
    middleware = FalconASGIOpenAPIMiddleware.from_spec(spec)
    app = App(middleware=[middleware])
    app.add_route("/v1/pets", PetListResource())
    client = TestClient(app)

    with pytest.warns(DeprecationWarning):
        response = client.simulate_get(
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


def test_explicit_asgi_middleware_validates_response(spec):
    middleware = FalconASGIOpenAPIMiddleware.from_spec(spec)
    app = App(middleware=[middleware])
    app.add_route("/v1/pets", InvalidPetListResource())
    client = TestClient(app)

    with pytest.warns(DeprecationWarning):
        response = client.simulate_get(
            "/v1/pets",
            host="petstore.swagger.io",
            query_string="limit=12",
        )

    assert response.status_code == 400
    assert "errors" in response.json
