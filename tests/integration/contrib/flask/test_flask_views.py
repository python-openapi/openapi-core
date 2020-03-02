from flask import Flask, make_response, jsonify
import pytest

from openapi_core.contrib.flask.views import FlaskOpenAPIView
from openapi_core.shortcuts import create_spec


class TestFlaskOpenAPIView(object):

    view_response = None

    @pytest.fixture
    def spec(self, factory):
        specfile = 'contrib/flask/data/v3.0/flask_factory.yaml'
        return create_spec(factory.spec_from_file(specfile))

    @pytest.fixture
    def app(self):
        app = Flask("__main__")
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        return app

    @pytest.yield_fixture
    def client(self, app):
        with app.test_client() as client:
            with app.app_context():
                yield client

    @pytest.fixture
    def view_func(self, spec):
        outer = self

        class MyView(FlaskOpenAPIView):
            def get(self, id):
                return outer.view_response
        return MyView.as_view('browse_details', spec)

    @pytest.fixture(autouse=True)
    def view(self, app, view_func):
        app.add_url_rule("/browse/<id>/", view_func=view_func)

    def test_invalid_content_type(self, client):
        self.view_response = make_response('success', 200)

        result = client.get('/browse/12/')

        assert result.status_code == 415
        assert result.json == {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.schema.media_types.exceptions."
                        "InvalidContentType'>"
                    ),
                    'status': 415,
                    'title': (
                        'Content for following mimetype not found: text/html'
                    )
                }
            ]
        }

    def test_server_error(self, client):
        result = client.get('/browse/12/', base_url='https://localhost')

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.schema.servers.exceptions."
                        "InvalidServer'>"
                    ),
                    'status': 500,
                    'title': (
                        'Invalid request server '
                        'https://localhost/browse/{id}/'
                    ),
                }
            ]
        }
        assert result.status_code == 500
        assert result.json == expected_data

    def test_endpoint_error(self, client):
        result = client.get('/browse/invalidparameter/')

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.casting.schemas.exceptions."
                        "CastError'>"
                    ),
                    'status': 400,
                    'title': (
                        "Failed to cast value invalidparameter to type integer"
                    )
                }
            ]
        }
        assert result.status_code == 400
        assert result.json == expected_data

    def test_valid(self, client):
        self.view_response = jsonify(data='data')

        result = client.get('/browse/12/')

        assert result.status_code == 200
        assert result.json == {
            'data': 'data',
        }
