"""OpenAPI core contrib django responses module"""
from werkzeug.datastructures import Headers


class DjangoOpenAPIResponse:
    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.content

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def headers(self):
        return Headers(self.response.headers.items())

    @property
    def mimetype(self):
        return self.response["Content-Type"]
