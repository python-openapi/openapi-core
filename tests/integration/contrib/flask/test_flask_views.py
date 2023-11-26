import pytest
from flask import jsonify
from flask import make_response

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core.contrib.flask.views import FlaskOpenAPIView


@pytest.fixture(scope="session")
def view_factory(schema_path):
    def create(
        methods=None,
        extra_media_type_deserializers=None,
        extra_format_validators=None,
    ):
        if methods is None:

            def get(view, id):
                return make_response("success", 200)

            methods = {
                "get": get,
            }
        MyView = type("MyView", (FlaskOpenAPIView,), methods)
        extra_media_type_deserializers = extra_media_type_deserializers or {}
        extra_format_validators = extra_format_validators or {}
        config = Config(
            extra_media_type_deserializers=extra_media_type_deserializers,
            extra_format_validators=extra_format_validators,
        )
        openapi = OpenAPI(schema_path, config=config)
        return MyView.as_view(
            "myview",
            openapi,
        )

    return create


class TestFlaskOpenAPIView:
    @pytest.fixture
    def client(self, client_factory, app):
        client = client_factory(app)
        with app.app_context():
            yield client

    def test_invalid_content_type(self, client, app, view_factory):
        def get(view, id):
            view_response = make_response("success", 200)
            view_response.headers["X-Rate-Limit"] = "12"
            return view_response

        view_func = view_factory({"get": get})
        app.add_url_rule("/browse/<id>/", view_func=view_func)

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

    def test_server_error(self, client, app, view_factory):
        view_func = view_factory()
        app.add_url_rule("/browse/<id>/", view_func=view_func)

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

    def test_operation_error(self, client, app, view_factory):
        def put(view, id):
            return make_response("success", 200)

        view_func = view_factory({"put": put})
        app.add_url_rule("/browse/<id>/", view_func=view_func)

        result = client.put("/browse/12/")

        expected_data = {
            "errors": [
                {
                    "class": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "OperationNotFound'>"
                    ),
                    "status": 405,
                    "title": (
                        "Operation put not found for "
                        "http://localhost/browse/{id}/"
                    ),
                }
            ]
        }
        assert result.status_code == 405
        assert result.json == expected_data

    def test_path_error(self, client, app, view_factory):
        view_func = view_factory()
        app.add_url_rule("/browse/", view_func=view_func)

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

    def test_endpoint_error(self, client, app, view_factory):
        view_func = view_factory()
        app.add_url_rule("/browse/<id>/", view_func=view_func)

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

    def test_missing_required_header(self, client, app, view_factory):
        def get(view, id):
            return jsonify(data="data")

        view_func = view_factory({"get": get})
        app.add_url_rule("/browse/<id>/", view_func=view_func)

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

    def test_valid(self, client, app, view_factory):
        def get(view, id):
            resp = jsonify(data="data")
            resp.headers["X-Rate-Limit"] = "12"
            return resp

        view_func = view_factory({"get": get})
        app.add_url_rule("/browse/<id>/", view_func=view_func)

        result = client.get("/browse/12/")

        assert result.status_code == 200
        assert result.json == {
            "data": "data",
        }
