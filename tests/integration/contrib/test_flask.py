from flask.wrappers import Request, Response
import pytest
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict
from werkzeug.routing import Map, Rule, Subdomain
from werkzeug.test import create_environ

from openapi_core.contrib.flask import (
    FlaskOpenAPIRequest, FlaskOpenAPIResponse,
)
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.datatypes import RequestParameters
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


@pytest.fixture
def environ_factory():
    return create_environ


@pytest.fixture
def map():
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
def request_factory(map, environ_factory):
    server_name = 'localhost'

    def create_request(method, path, subdomain=None, query_string=None):
        environ = environ_factory(query_string=query_string)
        req = Request(environ)
        urls = map.bind_to_environ(
            environ, server_name=server_name, subdomain=subdomain)
        req.url_rule, req.view_args = urls.match(
            path, method, return_rule=True)
        return req
    return create_request


@pytest.fixture
def response_factory():
    def create_response(data, status_code=200):
        return Response(data, status=status_code)
    return create_response


class TestFlaskOpenAPIRequest(object):

    def test_simple(self, request_factory, request):
        request = request_factory('GET', '/', subdomain='www')

        openapi_request = FlaskOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([])
        headers = EnvironHeaders(request.environ)
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.host_url == request.host_url
        assert openapi_request.path == request.path
        assert openapi_request.method == request.method.lower()
        assert openapi_request.path_pattern == request.path
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == request.mimetype

    def test_multiple_values(self, request_factory, request):
        request = request_factory(
            'GET', '/', subdomain='www', query_string='a=b&a=c')

        openapi_request = FlaskOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([
            ('a', 'b'), ('a', 'c'),
        ])
        headers = EnvironHeaders(request.environ)
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.host_url == request.host_url
        assert openapi_request.path == request.path
        assert openapi_request.method == request.method.lower()
        assert openapi_request.path_pattern == request.path
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == request.mimetype

    def test_url_rule(self, request_factory, request):
        request = request_factory('GET', '/browse/12/', subdomain='kb')

        openapi_request = FlaskOpenAPIRequest(request)

        path = {'id': 12}
        query = ImmutableMultiDict([])
        headers = EnvironHeaders(request.environ)
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.host_url == request.host_url
        assert openapi_request.path == request.path
        assert openapi_request.method == request.method.lower()
        assert openapi_request.path_pattern == '/browse/{id}/'
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == request.mimetype


class TestFlaskOpenAPIResponse(object):

    def test_invalid_server(self, response_factory):
        response = response_factory('Not Found', status_code=404)

        openapi_response = FlaskOpenAPIResponse(response)

        assert openapi_response.data == response.data
        assert openapi_response.status_code == response._status_code
        assert openapi_response.mimetype == response.mimetype


class TestFlaskOpenAPIValidation(object):

    @pytest.fixture
    def flask_spec(self, factory):
        specfile = 'data/v3.0/flask_factory.yaml'
        return create_spec(factory.spec_from_file(specfile))

    def test_response_validator_path_pattern(self,
                                             flask_spec,
                                             request_factory,
                                             response_factory):
        validator = ResponseValidator(flask_spec)
        request = request_factory('GET', '/browse/12/', subdomain='kb')
        openapi_request = FlaskOpenAPIRequest(request)
        response = response_factory('Some item', status_code=200)
        openapi_response = FlaskOpenAPIResponse(response)
        result = validator.validate(openapi_request, openapi_response)
        assert not result.errors

    def test_request_validator_path_pattern(self, flask_spec, request_factory):
        validator = RequestValidator(flask_spec)
        request = request_factory('GET', '/browse/12/', subdomain='kb')
        openapi_request = FlaskOpenAPIRequest(request)
        result = validator.validate(openapi_request)
        assert not result.errors
