from urllib.parse import urljoin

from werkzeug.datastructures import Headers, ImmutableMultiDict

from openapi_core.contrib.flask import FlaskOpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


class TestFlaskOpenAPIRequest:

    def test_simple(self, request_factory, request):
        request = request_factory('GET', '/', subdomain='www')

        openapi_request = FlaskOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([])
        headers = Headers(request.headers)
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.full_url_pattern == \
            urljoin(request.host_url, request.path)
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
        headers = Headers(request.headers)
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.full_url_pattern == \
            urljoin(request.host_url, request.path)
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == request.mimetype

    def test_url_rule(self, request_factory, request):
        request = request_factory('GET', '/browse/12/', subdomain='kb')

        openapi_request = FlaskOpenAPIRequest(request)

        path = {'id': 12}
        query = ImmutableMultiDict([])
        headers = Headers(request.headers)
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.full_url_pattern == \
            urljoin(request.host_url, '/browse/{id}/')
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == request.mimetype
