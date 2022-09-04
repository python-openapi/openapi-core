"""OpenAPI core contrib flask responses module"""
from werkzeug.datastructures import Headers


class FlaskOpenAPIResponse:
    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.data

    @property
    def status_code(self):
        return self.response._status_code

    @property
    def mimetype(self):
        return self.response.mimetype

    @property
    def headers(self):
        return Headers(self.response.headers)
