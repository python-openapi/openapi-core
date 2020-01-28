from falcon import Request, Response
from falcon.routing import DefaultRouter
from falcon.testing import create_environ
import pytest
from six import BytesIO


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
    router.add_route('/browse/<int:id>/', None)
    return router


@pytest.fixture
def request_factory(environ_factory, router):
    server_name = 'localhost'

    def create_request(method, path, subdomain=None, query_string=None):
        environ = environ_factory(method, path, server_name)
        options = None
        # return create_req(options=options, **environ)
        req = Request(environ, options)
        req.uri_template = router.find(path, req)
        return req
    return create_request


@pytest.fixture
def response_factory(environ_factory):
    def create_response(
            data, status_code=200, content_type='application/json'):
        options = {
            'content_type': content_type,
            'data': data,
            'status': status_code,
        }
        return Response(options)
    return create_response
