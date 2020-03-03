from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


class TestRequestsOpenAPIRequest(object):

    def test_simple(self, request_factory, request):
        request = request_factory('GET', '/', subdomain='www')

        openapi_request = RequestsOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([])
        headers = request.headers
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.full_url_pattern == 'http://localhost/'
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == 'application/json'

    def test_multiple_values(self, request_factory, request):
        request = request_factory(
            'GET', '/', subdomain='www', query_string='a=b&a=c')

        openapi_request = RequestsOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict([
            ('a', 'b'), ('a', 'c'),
        ])
        headers = request.headers
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.full_url_pattern == 'http://localhost/'
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == 'application/json'

    def test_url_rule(self, request_factory, request):
        request = request_factory('GET', '/browse/12/', subdomain='kb')

        openapi_request = RequestsOpenAPIRequest(request)

        # empty when not bound to spec
        path = {}
        query = ImmutableMultiDict([])
        headers = request.headers
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.full_url_pattern == \
            'http://localhost/browse/12/'
        assert openapi_request.body == request.data
        assert openapi_request.mimetype == 'application/json'
