"""OpenAPI core contrib starlette requests module"""
from typing import Optional

from asgiref.sync import AsyncToSync
from starlette.requests import Request

from openapi_core.datatypes import RequestParameters


class StarletteOpenAPIRequest:
    def __init__(self, request: Request):
        if not isinstance(request, Request):
            raise TypeError(f"'request' argument is not type of {Request}")
        self.request = request

        self.parameters = RequestParameters(
            query=self.request.query_params,
            header=self.request.headers,
            cookie=self.request.cookies,
        )

        self._get_body = AsyncToSync(self.request.body, force_new_loop=True)

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
        body = self._get_body()
        if body is None:
            return None
        if isinstance(body, bytes):
            return body
        assert isinstance(body, str)
        return body.encode("utf-8")

    @property
    def content_type(self) -> str:
        # default value according to RFC 2616
        return (
            self.request.headers.get("Content-Type")
            or "application/octet-stream"
        )
