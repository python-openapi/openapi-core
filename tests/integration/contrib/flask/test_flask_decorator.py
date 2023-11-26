import pytest
from flask import jsonify
from flask import make_response

from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
from openapi_core.datatypes import Parameters


@pytest.fixture(scope="session")
def decorator_factory(schema_path):
    def create(**kwargs):
        return FlaskOpenAPIViewDecorator.from_spec(schema_path, **kwargs)

    return create


@pytest.fixture(scope="session")
def view_factory(decorator_factory):
    def create(
        app, path, methods=None, view_response_callable=None, decorator=None
    ):
        decorator = decorator or decorator_factory()

        @app.route(path, methods=methods)
        @decorator
        def view(*args, **kwargs):
            return view_response_callable(*args, **kwargs)

        return view

    return create


class TestFlaskOpenAPIDecorator:
    @pytest.fixture
    def decorator(self, decorator_factory):
        return decorator_factory()

    def test_invalid_content_type(self, client, view_factory, app, decorator):
        def view_response_callable(*args, **kwargs):
            from flask.globals import request

            assert request.openapi
            assert not request.openapi.errors
            assert request.openapi.parameters == Parameters(
                path={
                    "id": 12,
                }
            )
            resp = make_response("success", 200)
            resp.headers["X-Rate-Limit"] = "12"
            return resp

        view_factory(
            app,
            "/browse/<id>/",
            ["GET", "PUT"],
            view_response_callable=view_response_callable,
            decorator=decorator,
        )
        result = client.get("/browse/12/")

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

    def test_server_error(self, client, view_factory, app, decorator):
        view_factory(
            app,
            "/browse/<id>/",
            ["GET", "PUT"],
            view_response_callable=None,
            decorator=decorator,
        )
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

    def test_operation_error(self, client, view_factory, app, decorator):
        view_factory(
            app,
            "/browse/<id>/",
            ["GET", "PUT"],
            view_response_callable=None,
            decorator=decorator,
        )
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

    def test_path_error(self, client, view_factory, app, decorator):
        view_factory(
            app,
            "/browse/",
            view_response_callable=None,
            decorator=decorator,
        )
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

    def test_endpoint_error(self, client, view_factory, app, decorator):
        view_factory(
            app,
            "/browse/<id>/",
            ["GET", "PUT"],
            view_response_callable=None,
            decorator=decorator,
        )
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
        assert result.json == expected_data

    def test_response_object_valid(self, client, view_factory, app, decorator):
        def view_response_callable(*args, **kwargs):
            from flask.globals import request

            assert request.openapi
            assert not request.openapi.errors
            assert request.openapi.parameters == Parameters(
                path={
                    "id": 12,
                }
            )
            resp = jsonify(data="data")
            resp.headers["X-Rate-Limit"] = "12"
            return resp

        view_factory(
            app,
            "/browse/<id>/",
            ["GET", "PUT"],
            view_response_callable=view_response_callable,
            decorator=decorator,
        )

        result = client.get("/browse/12/")

        assert result.status_code == 200
        assert result.json == {
            "data": "data",
        }

    def test_response_skip_validation(
        self, client, view_factory, app, decorator_factory
    ):
        def view_response_callable(*args, **kwargs):
            from flask.globals import request

            assert request.openapi
            assert not request.openapi.errors
            assert request.openapi.parameters == Parameters(
                path={
                    "id": 12,
                }
            )
            return make_response("success", 200)

        decorator = decorator_factory(response_cls=None)
        view_factory(
            app,
            "/browse/<id>/",
            ["GET", "PUT"],
            view_response_callable=view_response_callable,
            decorator=decorator,
        )

        result = client.get("/browse/12/")

        assert result.status_code == 200
        assert result.text == "success"

    @pytest.mark.parametrize(
        "response,expected_status,expected_headers",
        [
            # ((body, status, headers)) response tuple
            (
                ("Not found", 404, {"X-Rate-Limit": "12"}),
                404,
                {"X-Rate-Limit": "12"},
            ),
            # (body, status) response tuple
            (("Not found", 404), 404, {}),
            # (body, headers) response tuple
            (
                ({"data": "data"}, {"X-Rate-Limit": "12"}),
                200,
                {"X-Rate-Limit": "12"},
            ),
        ],
    )
    def test_tuple_valid(
        self,
        client,
        view_factory,
        app,
        decorator,
        response,
        expected_status,
        expected_headers,
    ):
        def view_response_callable(*args, **kwargs):
            from flask.globals import request

            assert request.openapi
            assert not request.openapi.errors
            assert request.openapi.parameters == Parameters(
                path={
                    "id": 12,
                }
            )
            return response

        view_factory(
            app,
            "/browse/<id>/",
            ["GET", "PUT"],
            view_response_callable=view_response_callable,
            decorator=decorator,
        )

        result = client.get("/browse/12/")

        assert result.status_code == expected_status
        expected_body = response[0]
        if isinstance(expected_body, str):
            assert result.text == expected_body
        else:
            assert result.json == expected_body
        assert dict(result.headers).items() >= expected_headers.items()
