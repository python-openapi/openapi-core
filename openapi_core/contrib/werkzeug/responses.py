"""OpenAPI core contrib werkzeug responses module"""

from itertools import tee

from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response


class WerkzeugOpenAPIResponse:
    def __init__(self, response: Response):
        if not isinstance(response, Response):
            raise TypeError(f"'response' argument is not type of {Response}")
        self.response = response

    @property
    def data(self) -> bytes:
        if not self.response.is_sequence:
            resp_iter1, resp_iter2 = tee(self.response.iter_encoded())
            self.response.response = resp_iter1
            return b"".join(resp_iter2)
        return self.response.get_data(as_text=False)

    @property
    def status_code(self) -> int:
        return self.response._status_code

    @property
    def content_type(self) -> str:
        return str(self.response.mimetype)

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers)
