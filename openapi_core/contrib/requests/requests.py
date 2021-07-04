"""OpenAPI core contrib requests requests module"""

from urllib.parse import parse_qs
from urllib.parse import urlparse

from requests import Request
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


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

        # Method
        method = request.method.lower()

        # Cookies
        cookie = {}
        if request._cookies is not None:
            # cookies are stored in a cookiejar object
            cookie = request._cookies.get_dict()

        # Preparing a request formats the URL with params, strip them out again
        o = urlparse(request.url)
        params = parse_qs(o.query)
        # extract the URL without query parameters
        url = o._replace(query=None).geturl()

        # Order matters because all python requests issued from a session
        # include Accept */* which does not necessarily match the content type
        mimetype = request.headers.get("Content-Type") or request.headers.get(
            "Accept"
        )

        # Headers - request.headers is not an instance of Headers
        # which is expected
        header = Headers(dict(request.headers))

        # Body
        # TODO: figure out if request._body_position is relevant
        body = request.body

        # Path gets deduced by path finder against spec
        parameters = RequestParameters(
            query=ImmutableMultiDict(params),
            header=header,
            cookie=cookie,
        )
        return OpenAPIRequest(
            full_url_pattern=url,
            method=method,
            parameters=parameters,
            body=body,
            mimetype=mimetype,
        )
