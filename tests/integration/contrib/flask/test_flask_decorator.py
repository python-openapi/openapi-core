from flask import Flask, make_response, jsonify
import pytest

from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.datatypes import RequestParameters


class TestFlaskOpenAPIDecorator(object):

    view_response_callable = None

    @pytest.fixture
    def spec(self, factory):
        specfile = 'contrib/flask/data/v3.0/flask_factory.yaml'
        return create_spec(factory.spec_from_file(specfile))

    @pytest.fixture
    def decorator(self, spec):
        return FlaskOpenAPIViewDecorator.from_spec(spec)

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
    def view_response(self):
        def view_response(*args, **kwargs):
            return self.view_response_callable(*args, **kwargs)
        return view_response

    @pytest.fixture(autouse=True)
    def details_view(self, app, decorator, view_response):
        @app.route("/browse/<id>/", methods=['GET', 'POST'])
        @decorator
        def browse_details(*args, **kwargs):
            return view_response(*args, **kwargs)
        return browse_details

    @pytest.fixture(autouse=True)
    def list_view(self, app, decorator, view_response):
        @app.route("/browse/")
        @decorator
        def browse_list(*args, **kwargs):
            return view_response(*args, **kwargs)
        return browse_list

    def test_invalid_content_type(self, client):
        def view_response_callable(*args, **kwargs):
            from flask.globals import request
            assert request.openapi
            assert not request.openapi.errors
            assert request.openapi.parameters == RequestParameters(path={
                'id': 12,
            })
            return make_response('success', 200)
        self.view_response_callable = view_response_callable
        result = client.get('/browse/12/')

        assert result.json == {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.templating.media_types."
                        "exceptions.MediaTypeNotFound'>"
                    ),
                    'status': 415,
                    'title': (
                        "Content for the following mimetype not found: "
                        "text/html. Valid mimetypes: ['application/json']"
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
                        "<class 'openapi_core.templating.paths.exceptions."
                        "ServerNotFound'>"
                    ),
                    'status': 400,
                    'title': (
                        'Server not found for '
                        'https://localhost/browse/{id}/'
                    ),
                }
            ]
        }
        assert result.status_code == 400
        assert result.json == expected_data

    def test_operation_error(self, client):
        result = client.post('/browse/12/')

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "OperationNotFound'>"
                    ),
                    'status': 405,
                    'title': (
                        'Operation post not found for '
                        'http://localhost/browse/{id}/'
                    ),
                }
            ]
        }
        assert result.status_code == 405
        assert result.json == expected_data

    def test_path_error(self, client):
        result = client.get('/browse/')

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "PathNotFound'>"
                    ),
                    'status': 404,
                    'title': (
                        'Path not found for '
                        'http://localhost/browse/'
                    ),
                }
            ]
        }
        assert result.status_code == 404
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
        assert result.json == expected_data

    def test_valid(self, client):
        def view_response_callable(*args, **kwargs):
            from flask.globals import request
            assert request.openapi
            assert not request.openapi.errors
            assert request.openapi.parameters == RequestParameters(path={
                'id': 12,
            })
            return jsonify(data='data')
        self.view_response_callable = view_response_callable

        result = client.get('/browse/12/')

        assert result.status_code == 200
        assert result.json == {
            'data': 'data',
        }
