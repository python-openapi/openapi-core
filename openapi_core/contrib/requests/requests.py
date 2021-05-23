"""OpenAPI core contrib requests requests module"""

from urllib.parse import urlparse, parse_qs

from werkzeug.datastructures import ImmutableMultiDict, Headers
from requests import Request

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)


class RequestsOpenAPIRequestFactory:

    @classmethod
    def create(cls, request):
        """
        Converts a requests request to an OpenAPI one

        Internally converts to a `PreparedRequest` first to parse the exact
        payload being sent
        """
        if isinstance(request, Request):
            request = request.prepare()

        # Cookies
        cookie = {}
        if request._cookies is not None:
            # cookies are stored in a cookiejar object
            cookie = request._cookies.get_dict()
        params_cookie: ImmutableMultiDict = ImmutableMultiDict(cookie)
        # Preparing a request formats the URL with params, strip them out again
        o = urlparse(request.url)
        params_query: ImmutableMultiDict = ImmutableMultiDict(
            parse_qs(o.query))
        # Headers - request.headers is not an instance of Headers
        # which is expected
        params_header: Headers = Headers(dict(request.headers))
        # Path gets deduced by path finder against spec
        req_parameters = RequestParameters(
            query=params_query,
            header=params_header,
            cookie=params_cookie,
        )

        # extract the URL without query parameters
        req_full_url_pattern: str = o._replace(query=None).geturl()
        # Method
        req_method = request.method.lower()
        # Body
        # TODO: figure out if request._body_position is relevant
        req_body: str = request.body
        # Order matters because all python requests issued from a session
        # include Accept */* which does not necessarily match the content type
        req_mimetype: str = request.headers.get('Content-Type') or \
            request.headers.get('Accept')
        return OpenAPIRequest(
            full_url_pattern=req_full_url_pattern,
            method=req_method,
            parameters=req_parameters,
            body=req_body,
            mimetype=req_mimetype,
        )
