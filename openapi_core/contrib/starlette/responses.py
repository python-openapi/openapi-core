"""OpenAPI core contrib starlette responses module"""
from starlette.datastructures import Headers
from starlette.responses import Response


class StarletteOpenAPIResponse:
    def __init__(self, response: Response):
        self.response = response

    @property
    def data(self) -> str:
        if isinstance(self.response.body, bytes):
            return self.response.body.decode("utf-8")
        assert isinstance(self.response.body, str)
        return self.response.body

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def mimetype(self) -> str:
        return self.response.media_type or ""

    @property
    def headers(self) -> Headers:
        return self.response.headers
