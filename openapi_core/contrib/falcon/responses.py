"""OpenAPI core contrib falcon responses module"""

from itertools import tee

from falcon.response import Response
from werkzeug.datastructures import Headers


class FalconOpenAPIResponse:
    def __init__(self, response: Response):
        if not isinstance(response, Response):
            raise TypeError(f"'response' argument is not type of {Response}")
        self.response = response

    @property
    def data(self) -> bytes:
        if self.response.text is None:
            if self.response.stream is None:
                return b""
            resp_iter1, resp_iter2 = tee(self.response.stream)
            self.response.stream = resp_iter1
            content = b"".join(resp_iter2)
            return content
        assert isinstance(self.response.text, str)
        return self.response.text.encode("utf-8")

    @property
    def status_code(self) -> int:
        return int(self.response.status[:3])

    @property
    def content_type(self) -> str:
        content_type = ""
        if self.response.content_type:
            content_type = self.response.content_type
        else:
            content_type = self.response.options.default_media_type
        return content_type

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers)
