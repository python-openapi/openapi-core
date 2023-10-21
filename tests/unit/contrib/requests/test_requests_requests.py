import pytest
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.datatypes import RequestParameters


class TestRequestsOpenAPIRequest:
    def test_type_invalid(self):
        with pytest.raises(TypeError):
            RequestsOpenAPIRequest(None)

    def test_simple(self, request_factory, request):
        request = request_factory("GET", "/", subdomain="www")

        openapi_request = RequestsOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([])
        headers = Headers(dict(request.headers))
        cookies = {}
        prepared = request.prepare()
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == "http://localhost"
        assert openapi_request.path == "/"
        assert openapi_request.body == prepared.body
        assert openapi_request.content_type == "application/json"

    def test_multiple_values(self, request_factory, request):
        request = request_factory(
            "GET", "/", subdomain="www", query_string="a=b&a=c"
        )

        openapi_request = RequestsOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict(
            [
                ("a", "b"),
                ("a", "c"),
            ]
        )
        headers = Headers(dict(request.headers))
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        prepared = request.prepare()
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == "http://localhost"
        assert openapi_request.path == "/"
        assert openapi_request.body == prepared.body
        assert openapi_request.content_type == "application/json"

    def test_url_rule(self, request_factory, request):
        request = request_factory("GET", "/browse/12/", subdomain="kb")

        openapi_request = RequestsOpenAPIRequest(request)

        # empty when not bound to spec
        path = {}
        query = ImmutableMultiDict([])
        headers = Headers(
            {
                "Content-Type": "application/json",
            }
        )
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        prepared = request.prepare()
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == "http://localhost"
        assert openapi_request.path == "/browse/12/"
        assert openapi_request.body == prepared.body
        assert openapi_request.content_type == "application/json"

    def test_hash_param(self, request_factory, request):
        request = request_factory("GET", "/browse/#12", subdomain="kb")

        openapi_request = RequestsOpenAPIRequest(request)

        # empty when not bound to spec
        path = {}
        query = ImmutableMultiDict([])
        headers = Headers(
            {
                "Content-Type": "application/json",
            }
        )
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        prepared = request.prepare()
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == "http://localhost"
        assert openapi_request.path == "/browse/#12"
        assert openapi_request.body == prepared.body
        assert openapi_request.content_type == "application/json"

    def test_content_type_with_charset(self, request_factory, request):
        request = request_factory(
            "GET",
            "/",
            subdomain="www",
            content_type="application/json; charset=utf-8",
        )

        openapi_request = RequestsOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([])
        headers = Headers(dict(request.headers))
        cookies = {}
        prepared = request.prepare()
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == "http://localhost"
        assert openapi_request.path == "/"
        assert openapi_request.body == prepared.body
        assert (
            openapi_request.content_type == "application/json; charset=utf-8"
        )
