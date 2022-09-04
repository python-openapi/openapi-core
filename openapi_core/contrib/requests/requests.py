"""OpenAPI core contrib requests requests module"""

from urllib.parse import parse_qs
from urllib.parse import urlparse

from requests import Request
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import RequestParameters


class RequestsOpenAPIRequest:
    """
    Converts a requests request to an OpenAPI one

    Internally converts to a `PreparedRequest` first to parse the exact
    payload being sent
    """

    def __init__(self, request):
        if isinstance(request, Request):
            request = request.prepare()

        self.request = request
        self._url_parsed = urlparse(request.url)

        cookie = {}
        if self.request._cookies is not None:
            # cookies are stored in a cookiejar object
            cookie = self.request._cookies.get_dict()

        self.parameters = RequestParameters(
            query=ImmutableMultiDict(parse_qs(self._url_parsed.query)),
            header=Headers(dict(self.request.headers)),
            cookie=cookie,
        )

    @property
    def host_url(self):
        return f"{self._url_parsed.scheme}://{self._url_parsed.netloc}"

    @property
    def path(self):
        return self._url_parsed.path

    @property
    def method(self):
        return self.request.method.lower()

    @property
    def body(self):
        # TODO: figure out if request._body_position is relevant
        return self.request.body

    @property
    def mimetype(self):
        # Order matters because all python requests issued from a session
        # include Accept */* which does not necessarily match the content type
        return self.request.headers.get(
            "Content-Type"
        ) or self.request.headers.get("Accept")
