"""OpenAPI core contrib werkzeug responses module"""
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response


class WerkzeugOpenAPIResponse:
    def __init__(self, response: Response):
        self.response = response

    @property
    def data(self) -> str:
        return self.response.get_data(as_text=True)

    @property
    def status_code(self) -> int:
        return self.response._status_code

    @property
    def mimetype(self) -> str:
        return str(self.response.mimetype)

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers)
