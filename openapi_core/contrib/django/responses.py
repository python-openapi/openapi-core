"""OpenAPI core contrib django responses module"""

from itertools import tee

from django.http.response import HttpResponse
from django.http.response import StreamingHttpResponse
from werkzeug.datastructures import Headers


class DjangoOpenAPIResponse:
    def __init__(self, response: HttpResponse):
        if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
            raise TypeError(
                f"'response' argument is not type of {HttpResponse} or {StreamingHttpResponse}"
            )
        self.response = response

    @property
    def data(self) -> bytes:
        if isinstance(self.response, StreamingHttpResponse):
            resp_iter1, resp_iter2 = tee(self.response._iterator)
            self.response.streaming_content = resp_iter1
            content = b"".join(map(self.response.make_bytes, resp_iter2))
            return content
        assert isinstance(self.response.content, bytes)
        return self.response.content

    @property
    def status_code(self) -> int:
        assert isinstance(self.response.status_code, int)
        return self.response.status_code

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers.items())

    @property
    def content_type(self) -> str:
        content_type = self.response.get("Content-Type", "")
        assert isinstance(content_type, str)
        return content_type
