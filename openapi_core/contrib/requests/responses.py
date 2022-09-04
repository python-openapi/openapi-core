"""OpenAPI core contrib requests responses module"""
from werkzeug.datastructures import Headers


class RequestsOpenAPIResponse:
    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.content

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def mimetype(self):
        return self.response.headers.get("Content-Type")

    @property
    def headers(self):
        return Headers(dict(self.response.headers))
