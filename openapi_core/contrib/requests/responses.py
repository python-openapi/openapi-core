"""OpenAPI core contrib requests responses module"""
from requests import Response
from werkzeug.datastructures import Headers


class RequestsOpenAPIResponse:
    def __init__(self, response: Response):
        if not isinstance(response, Response):
            raise TypeError(f"'response' argument is not type of {Response}")
        self.response = response

    @property
    def data(self) -> str:
        assert isinstance(self.response.content, bytes)
        return self.response.content.decode("utf-8")

    @property
    def status_code(self) -> int:
        return int(self.response.status_code)

    @property
    def mimetype(self) -> str:
        return str(self.response.headers.get("Content-Type", ""))

    @property
    def headers(self) -> Headers:
        return Headers(dict(self.response.headers))
