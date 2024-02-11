"""OpenAPI core contrib starlette responses module"""

from typing import Optional

from starlette.datastructures import Headers
from starlette.responses import Response
from starlette.responses import StreamingResponse


class StarletteOpenAPIResponse:
    def __init__(self, response: Response, data: Optional[bytes] = None):
        if not isinstance(response, Response):
            raise TypeError(f"'response' argument is not type of {Response}")
        self.response = response

        if data is None and isinstance(response, StreamingResponse):
            raise RuntimeError(
                f"'data' argument is required for {StreamingResponse}"
            )
        self._data = data

    @property
    def data(self) -> bytes:
        if self._data is not None:
            return self._data
        if isinstance(self.response.body, bytes):
            return self.response.body
        assert isinstance(self.response.body, str)
        return self.response.body.encode("utf-8")

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def content_type(self) -> str:
        return self.response.headers.get("Content-Type") or ""

    @property
    def headers(self) -> Headers:
        return self.response.headers
