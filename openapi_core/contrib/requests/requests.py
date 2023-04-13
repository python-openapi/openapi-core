"""OpenAPI core contrib requests requests module"""
from typing import Mapping
from typing import Optional
from typing import Union
from urllib.parse import parse_qs
from urllib.parse import urlparse

from requests import PreparedRequest
from requests import Request
from requests.cookies import RequestsCookieJar
from requests.utils import rewind_body
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.requests.protocols import SupportsCookieJar
from openapi_core.datatypes import RequestParameters


class RequestsOpenAPIRequest:
    """
    Converts a requests request to an OpenAPI request

    Internally converts to a `PreparedRequest` first to parse the exact
    payload being sent
    """

    def __init__(self, request: Union[Request, PreparedRequest]):
        if not isinstance(request, (Request, PreparedRequest)):
            raise TypeError(
                "'request' argument is not type of "
                f"{Request} or {PreparedRequest}"
            )
        self._request = None
        if isinstance(request, Request):
            self._request = request
            request = request.prepare()

        self.request = request
        if request.url is None:
            raise RuntimeError("Request URL is missing")
        self._url_parsed = urlparse(request.url, allow_fragments=False)

        cookie = {}
        if isinstance(self.request, SupportsCookieJar) and isinstance(
            self.request._cookies, RequestsCookieJar
        ):
            # cookies are stored in a cookiejar object
            cookie = self.request._cookies.get_dict()

        self.parameters = RequestParameters(
            query=ImmutableMultiDict(parse_qs(self._url_parsed.query)),
            header=Headers(dict(self.request.headers)),
            cookie=ImmutableMultiDict(cookie),
        )

    @property
    def host_url(self) -> str:
        return f"{self._url_parsed.scheme}://{self._url_parsed.netloc}"

    @property
    def path(self) -> str:
        assert isinstance(self._url_parsed.path, str)
        return self._url_parsed.path

    @property
    def method(self) -> str:
        method = self.request.method
        return method and method.lower() or ""

    @property
    def body(self) -> Optional[str]:
        import ipdb; ipdb.set_trace()
        body = self.request.body
        if body is None:
            return None
        chunks = None
        is_stream = all(
            [
                hasattr(body, "__iter__"),
                not isinstance(body, (bytes, str, list, tuple, Mapping)),
            ]
        )
        if is_stream:
            chunks = list(body)
            body = b"".join(chunks)
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        assert isinstance(body, str)
        # recreate request stream from evaluated chunks
        if chunks is not None:
            self.request.body = (x for x in chunks)
        # TODO: figure out if request._body_position is relevant
        return body

    @property
    def mimetype(self) -> str:
        # Order matters because all python requests issued from a session
        # include Accept */* which does not necessarily match the content type
        return str(
            self.request.headers.get("Content-Type")
            or self.request.headers.get("Accept")
        ).split(";")[0]


class RequestsOpenAPIWebhookRequest(RequestsOpenAPIRequest):
    """
    Converts a requests request to an OpenAPI Webhook request

    Internally converts to a `PreparedRequest` first to parse the exact
    payload being sent
    """

    def __init__(self, request: Union[Request, PreparedRequest], name: str):
        super().__init__(request)
        self.name = name
