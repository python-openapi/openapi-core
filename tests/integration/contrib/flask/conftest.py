import pytest
from flask.wrappers import Request
from flask.wrappers import Response
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.routing import Subdomain
from werkzeug.test import create_environ


@pytest.fixture
def environ_factory():
    return create_environ


@pytest.fixture
def map():
    return Map(
        [
            # Static URLs
            Rule("/", endpoint="static/index"),
            Rule("/about", endpoint="static/about"),
            Rule("/help", endpoint="static/help"),
            # Knowledge Base
            Subdomain(
                "kb",
                [
                    Rule("/", endpoint="kb/index"),
                    Rule("/browse/", endpoint="kb/browse"),
                    Rule("/browse/<int:id>/", endpoint="kb/browse"),
                    Rule("/browse/<int:id>/<int:page>", endpoint="kb/browse"),
                ],
            ),
        ],
        default_subdomain="www",
    )


@pytest.fixture
def request_factory(map, environ_factory):
    server_name = "localhost"

    def create_request(method, path, subdomain=None, query_string=None):
        environ = environ_factory(query_string=query_string)
        req = Request(environ)
        urls = map.bind_to_environ(
            environ, server_name=server_name, subdomain=subdomain
        )
        req.url_rule, req.view_args = urls.match(
            path, method, return_rule=True
        )
        return req

    return create_request


@pytest.fixture
def response_factory():
    def create_response(
        data, status_code=200, headers=None, content_type="application/json"
    ):
        return Response(
            data,
            status=status_code,
            headers=headers,
            content_type=content_type,
        )

    return create_response
