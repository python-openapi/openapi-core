from json import dumps

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask.wrappers import Response

from openapi_core import V30RequestUnmarshaller
from openapi_core.contrib.flask import FlaskOpenAPIRequest


class TestWerkzeugOpenAPIValidation:
    @pytest.fixture
    def spec(self, factory):
        specfile = "contrib/requests/data/v3.0/requests_factory.yaml"
        return factory.spec_from_file(specfile)

    @pytest.fixture
    def app(self):
        app = Flask("__main__", root_path="/browse")
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def details_view_func(self, spec):
        def datails_browse(id):
            from flask import request

            openapi_request = FlaskOpenAPIRequest(request)
            unmarshaller = V30RequestUnmarshaller(spec)
            result = unmarshaller.unmarshal(openapi_request)
            assert not result.errors

            if request.args.get("q") == "string":
                return Response(
                    dumps({"data": "data"}),
                    headers={"X-Rate-Limit": "12"},
                    mimetype="application/json",
                    status=200,
                )
            else:
                return Response("Not Found", status=404)

        return datails_browse

    @pytest.fixture(autouse=True)
    def view(self, app, details_view_func):
        app.add_url_rule(
            "/<id>/",
            view_func=details_view_func,
            methods=["POST"],
        )

    @pytest.fixture
    def client(self, app):
        return FlaskClient(app)

    def test_request_validator_root_path(self, client):
        query_string = {
            "q": "string",
        }
        headers = {"content-type": "application/json"}
        data = {"param1": 1}
        result = client.post(
            "/12/",
            base_url="http://localhost/browse",
            query_string=query_string,
            json=data,
            headers=headers,
        )

        assert result.status_code == 200
        assert result.json == {"data": "data"}
