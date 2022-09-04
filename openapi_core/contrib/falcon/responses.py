"""OpenAPI core contrib falcon responses module"""
from werkzeug.datastructures import Headers


class FalconOpenAPIResponse:
    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.text

    @property
    def status_code(self):
        return int(self.response.status[:3])

    @property
    def mimetype(self):
        mimetype = ""
        if self.response.content_type:
            mimetype = self.response.content_type.partition(";")[0]
        else:
            mimetype = self.response.options.default_media_type
        return mimetype

    @property
    def headers(self):
        return Headers(self.response.headers)
