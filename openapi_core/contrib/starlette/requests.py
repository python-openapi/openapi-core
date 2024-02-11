"""OpenAPI core contrib starlette requests module"""

from typing import Optional

from starlette.requests import Request

from openapi_core.datatypes import RequestParameters


class StarletteOpenAPIRequest:
    def __init__(self, request: Request, body: Optional[bytes] = None):
        if not isinstance(request, Request):
            raise TypeError(f"'request' argument is not type of {Request}")
        self.request = request

        self.parameters = RequestParameters(
            query=self.request.query_params,
            header=self.request.headers,
            cookie=self.request.cookies,
        )

        self._body = body

    @property
    def host_url(self) -> str:
        return self.request.base_url._url

    @property
    def path(self) -> str:
        return self.request.url.path

    @property
    def method(self) -> str:
        return self.request.method.lower()

    @property
    def body(self) -> Optional[bytes]:
        return self._body

    @property
    def content_type(self) -> str:
        # default value according to RFC 2616
        return (
            self.request.headers.get("Content-Type")
            or "application/octet-stream"
        )
