from falcon import Request, Response, RequestOptions, ResponseOptions
from falcon.routing import DefaultRouter
from falcon.status_codes import HTTP_200
from falcon.testing import create_environ
import pytest


@pytest.fixture
def environ_factory():
    def create_env(method, path, server_name):
        return create_environ(
            host=server_name,
            path=path,
        )
    return create_env


@pytest.fixture
def router():
    router = DefaultRouter()
    router.add_route("/browse/{id:int}/", lambda x: x)
    return router


@pytest.fixture
def request_factory(environ_factory, router):
    server_name = 'localhost'

    def create_request(
            method, path, subdomain=None, query_string=None,
            content_type='application/json'):
        environ = environ_factory(method, path, server_name)
        options = RequestOptions()
        # return create_req(options=options, **environ)
        req = Request(environ, options)
        return req
    return create_request


@pytest.fixture
def response_factory(environ_factory):
    def create_response(
            data, status_code=200, headers=None,
            content_type='application/json'):
        options = ResponseOptions()
        resp = Response(options)
        resp.body = data
        resp.content_type = content_type
        resp.status = HTTP_200
        resp.set_headers(headers or {})
        return resp
    return create_response
