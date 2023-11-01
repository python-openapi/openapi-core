"""OpenAPI core contrib aiohttp responses module"""

import multidict
from aiohttp import web


class AIOHTTPOpenAPIWebResponse:
    def __init__(self, response: web.Response):
        if not isinstance(response, web.Response):
            raise TypeError(
                f"'response' argument is not type of {web.Response.__qualname__!r}"
            )
        self.response = response

    @property
    def data(self) -> bytes:
        if self.response.body is None:
            return b""
        if isinstance(self.response.body, bytes):
            return self.response.body
        assert isinstance(self.response.body, str)
        return self.response.body.encode("utf-8")

    @property
    def status_code(self) -> int:
        return self.response.status

    @property
    def content_type(self) -> str:
        return self.response.content_type or ""

    @property
    def headers(self) -> multidict.CIMultiDict[str]:
        return self.response.headers
