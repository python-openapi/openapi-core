from json import dumps
from pathlib import Path

import pytest
import yaml
from falcon import App
from falcon.constants import MEDIA_JSON
from falcon.status_codes import HTTP_200
from falcon.testing import TestClient
from jsonschema_path import SchemaPath

from openapi_core.contrib.falcon.middlewares import FalconWSGIOpenAPIMiddleware


@pytest.fixture
def spec():
    openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
    spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
    return SchemaPath.from_dict(spec_dict)


class PetListResource:
    def on_get(self, req, resp):
        assert req.context.openapi
        assert not req.context.openapi.errors
        resp.status = HTTP_200
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


def test_explicit_wsgi_middleware_works(spec):
    middleware = FalconWSGIOpenAPIMiddleware.from_spec(spec)
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
