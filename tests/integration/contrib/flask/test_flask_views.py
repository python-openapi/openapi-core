import pytest
from flask import Flask
from flask import jsonify
from flask import make_response

from openapi_core.contrib.flask.views import FlaskOpenAPIView


class TestFlaskOpenAPIView:
    view_response = None

    @pytest.fixture
    def spec(self, factory):
        specfile = "contrib/flask/data/v3.0/flask_factory.yaml"
        return factory.spec_from_file(specfile)

    @pytest.fixture
    def app(self):
        app = Flask("__main__")
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, app):
        with app.test_client() as client:
            with app.app_context():
                yield client

    @pytest.fixture
    def details_view_func(self, spec):
        outer = self

        class MyDetailsView(FlaskOpenAPIView):
            def get(self, id):
                return outer.view_response

            def post(self, id):
                return outer.view_response

        return MyDetailsView.as_view("browse_details", spec)

    @pytest.fixture
    def list_view_func(self, spec):
        outer = self

        class MyListView(FlaskOpenAPIView):
            def get(self):
                return outer.view_response

        return MyListView.as_view("browse_list", spec)

    @pytest.fixture(autouse=True)
    def view(self, app, details_view_func, list_view_func):
        app.add_url_rule("/browse/<id>/", view_func=details_view_func)
        app.add_url_rule("/browse/", view_func=list_view_func)

    def test_invalid_content_type(self, client):
        self.view_response = make_response("success", 200)
        self.view_response.headers["X-Rate-Limit"] = "12"

        result = client.get("/browse/12/")

        assert result.status_code == 415
        assert result.json == {
            "errors": [
                {
                    "class": (
                        "<class 'openapi_core.templating.media_types."
                        "exceptions.MediaTypeNotFound'>"
                    ),
                    "status": 415,
                    "title": (
                        "Content for the following mimetype not found: "
                        "text/html. Valid mimetypes: ['application/json']"
                    ),
                }
            ]
        }

    def test_server_error(self, client):
        result = client.get("/browse/12/", base_url="https://localhost")

        expected_data = {
            "errors": [
                {
                    "class": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "ServerNotFound'>"
                    ),
                    "status": 400,
                    "title": (
                        "Server not found for "
                        "https://localhost/browse/{id}/"
                    ),
                }
            ]
        }
        assert result.status_code == 400
        assert result.json == expected_data

    def test_operation_error(self, client):
        result = client.post("/browse/12/")

        expected_data = {
            "errors": [
                {
                    "class": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "OperationNotFound'>"
                    ),
                    "status": 405,
                    "title": (
                        "Operation post not found for "
                        "http://localhost/browse/{id}/"
                    ),
                }
            ]
        }
        assert result.status_code == 405
        assert result.json == expected_data

    def test_path_error(self, client):
        result = client.get("/browse/")

        expected_data = {
            "errors": [
                {
                    "class": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "PathNotFound'>"
                    ),
                    "status": 404,
                    "title": (
                        "Path not found for " "http://localhost/browse/"
                    ),
                }
            ]
        }
        assert result.status_code == 404
        assert result.json == expected_data

    def test_endpoint_error(self, client):
        result = client.get("/browse/invalidparameter/")

        expected_data = {
            "errors": [
                {
                    "class": (
                        "<class 'openapi_core.casting.schemas.exceptions."
                        "CastError'>"
                    ),
                    "status": 400,
                    "title": (
                        "Failed to cast value to integer type: "
                        "invalidparameter"
                    ),
                }
            ]
        }
        assert result.status_code == 400
        assert result.json == expected_data

    def test_missing_required_header(self, client):
        self.view_response = jsonify(data="data")

        result = client.get("/browse/12/")

        expected_data = {
            "errors": [
                {
                    "class": (
                        "<class 'openapi_core.validation.response.exceptions."
                        "MissingRequiredHeader'>"
                    ),
                    "status": 400,
                    "title": ("Missing required header: X-Rate-Limit"),
                }
            ]
        }
        assert result.status_code == 400
        assert result.json == expected_data

    def test_valid(self, client):
        self.view_response = jsonify(data="data")
        self.view_response.headers["X-Rate-Limit"] = "12"

        result = client.get("/browse/12/")

        assert result.status_code == 200
        assert result.json == {
            "data": "data",
        }
