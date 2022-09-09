"""OpenAPI core contrib django responses module"""
from django.http.response import HttpResponse
from werkzeug.datastructures import Headers


class DjangoOpenAPIResponse:
    def __init__(self, response: HttpResponse):
        self.response = response

    @property
    def data(self) -> str:
        assert isinstance(self.response.content, bytes)
        return self.response.content.decode("utf-8")

    @property
    def status_code(self) -> int:
        assert isinstance(self.response.status_code, int)
        return self.response.status_code

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers.items())

    @property
    def mimetype(self) -> str:
        content_type = self.response.get("Content-Type", "")
        assert isinstance(content_type, str)
        return content_type
