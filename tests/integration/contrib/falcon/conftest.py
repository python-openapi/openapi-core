import os
import sys

import pytest
from falcon import Request
from falcon import RequestOptions
from falcon import Response
from falcon import ResponseOptions
from falcon.routing import DefaultRouter
from falcon.status_codes import HTTP_200
from falcon.testing import TestClient
from falcon.testing import create_environ


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
    server_name = "localhost"

    def create_request(
        method,
        path,
        subdomain=None,
        query_string=None,
        content_type="application/json",
    ):
        environ = environ_factory(method, path, server_name)
        options = RequestOptions()
        # return create_req(options=options, **environ)
        req = Request(environ, options)
        return req

    return create_request


@pytest.fixture
def response_factory(environ_factory):
    def create_response(
        data, status_code=200, headers=None, content_type="application/json"
    ):
        options = ResponseOptions()
        resp = Response(options)
        resp.body = data
        resp.content_type = content_type
        resp.status = HTTP_200
        resp.set_headers(headers or {})
        return resp

    return create_response


@pytest.fixture(autouse=True, scope="module")
def falcon_setup():
    directory = os.path.abspath(os.path.dirname(__file__))
    falcon_project_dir = os.path.join(directory, "data/v3.0")
    sys.path.insert(0, falcon_project_dir)
    yield
    sys.path.remove(falcon_project_dir)


@pytest.fixture
def app():
    from falconproject.__main__ import app

    return app


@pytest.fixture
def client(app):
    return TestClient(app)
