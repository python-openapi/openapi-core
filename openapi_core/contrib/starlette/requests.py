"""OpenAPI core contrib starlette requests module"""
from typing import Optional

from asgiref.sync import AsyncToSync
from starlette.requests import Request

from openapi_core.validation.request.datatypes import RequestParameters


class StarletteOpenAPIRequest:
    def __init__(self, request: Request):
        self.request = request

        self.parameters = RequestParameters(
            query=self.request.query_params,
            header=self.request.headers,
            cookie=self.request.cookies,
        )

        self._get_body = AsyncToSync(self.request.body, force_new_loop=True)  # type: ignore

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
    def body(self) -> Optional[str]:
        body = self._get_body()
        if body is None:
            return None
        if isinstance(body, bytes):
            return body.decode("utf-8")
        assert isinstance(body, str)
        return body

    @property
    def mimetype(self) -> str:
        content_type = self.request.headers["Content-Type"]
        if content_type:
            return content_type.partition(";")[0]

        return ""
