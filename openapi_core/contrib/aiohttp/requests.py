"""OpenAPI core contrib aiohttp requests module"""

from __future__ import annotations

from aiohttp import web

from openapi_core.datatypes import RequestParameters


class Empty: ...


_empty = Empty()


class AIOHTTPOpenAPIWebRequest:
    __slots__ = ("request", "parameters", "_get_body", "_body")

    def __init__(self, request: web.Request, *, body: bytes | None):
        if not isinstance(request, web.Request):
            raise TypeError(
                f"'request' argument is not type of {web.Request.__qualname__!r}"
            )
        self.request = request
        self.parameters = RequestParameters(
            query=self.request.query,
            header=self.request.headers,
            cookie=self.request.cookies,
        )
        self._body = body

    @property
    def host_url(self) -> str:
        return f"{self.request.url.scheme}://{self.request.url.host}"

    @property
    def path(self) -> str:
        return self.request.url.path

    @property
    def method(self) -> str:
        return self.request.method.lower()

    @property
    def body(self) -> bytes | None:
        return self._body

    @property
    def content_type(self) -> str:
        return self.request.content_type
