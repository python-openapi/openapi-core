"""OpenAPI core contrib falcon responses module"""
from falcon.response import Response
from werkzeug.datastructures import Headers


class FalconOpenAPIResponse:
    def __init__(self, response: Response):
        if not isinstance(response, Response):
            raise TypeError(f"'response' argument is not type of {Response}")
        self.response = response

    @property
    def data(self) -> str:
        if self.response.text is None:
            return ""
        assert isinstance(self.response.text, str)
        return self.response.text

    @property
    def status_code(self) -> int:
        return int(self.response.status[:3])

    @property
    def mimetype(self) -> str:
        mimetype = ""
        if self.response.content_type:
            mimetype = self.response.content_type.partition(";")[0]
        else:
            mimetype = self.response.options.default_media_type
        return mimetype

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers)
