import pytest

from flask.wrappers import Request, Response
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict
from werkzeug.routing import Map, Rule, Subdomain
from werkzeug.test import create_environ

from openapi_core.wrappers import FlaskOpenAPIRequest, FlaskOpenAPIResponse


class TestFlaskOpenAPIRequest(object):

    server_name = 'localhost'

    @pytest.fixture
    def environ(self):
        return create_environ()

    @pytest.fixture
    def map(self):
        return Map([
            # Static URLs
            Rule('/', endpoint='static/index'),
            Rule('/about', endpoint='static/about'),
            Rule('/help', endpoint='static/help'),
            # Knowledge Base
            Subdomain('kb', [
                Rule('/', endpoint='kb/index'),
                Rule('/browse/', endpoint='kb/browse'),
                Rule('/browse/<int:id>/', endpoint='kb/browse'),
                Rule('/browse/<int:id>/<int:page>', endpoint='kb/browse')
            ])
        ], default_subdomain='www')

    @pytest.fixture
    def request_factory(self, map, environ):
        def create_request(method, path, subdomain=None):
            req = Request(environ)
            urls = map.bind_to_environ(
                environ, server_name=self.server_name, subdomain=subdomain)
            req.url_rule, req.view_args = urls.match(
                path, method, return_rule=True)
            return req
        return create_request

    @pytest.fixture
    def openapi_request(self, request):
        return FlaskOpenAPIRequest(request)

    def test_simple(self, request_factory, environ, request):
        request = request_factory('GET', '/', subdomain='www')

        openapi_request = FlaskOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([])
        headers = EnvironHeaders(environ)
        cookies = {}
        assert openapi_request.parameters == {
            'path': path,
            'query': query,
            'headers': headers,
            'cookies': cookies,
        }
        assert openapi_request.host_url == request.host_url
        assert openapi_request.path == request.path
        assert openapi_request.method == request.method.lower()
        assert openapi_request.path_pattern == request.path
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == request.mimetype

    def test_url_rule(self, request_factory, environ, request):
        request = request_factory('GET', '/browse/12/', subdomain='kb')

        openapi_request = FlaskOpenAPIRequest(request)

        path = {'id': 12}
        query = ImmutableMultiDict([])
        headers = EnvironHeaders(environ)
        cookies = {}
        assert openapi_request.parameters == {
            'path': path,
            'query': query,
            'headers': headers,
            'cookies': cookies,
        }
        assert openapi_request.host_url == request.host_url
        assert openapi_request.path == request.path
        assert openapi_request.method == request.method.lower()
        assert openapi_request.path_pattern == request.url_rule.rule
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == request.mimetype


class TetsFlaskOpenAPIResponse(object):

    @pytest.fixture
    def response_factory(self):
        def create_response(body, status=200):
            return Response('Not Found', status=404)
        return create_response

    def test_invalid_server(self, response_factory):
        response = response_factory('Not Found', status=404)

        openapi_response = FlaskOpenAPIResponse(response)

        assert openapi_response.body == response.text
        assert openapi_response.status == response.status
        assert openapi_response.mimetype == response.mimetype
