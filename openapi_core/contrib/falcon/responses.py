"""OpenAPI core contrib falcon responses module"""

import inspect
from io import BytesIO
from itertools import tee
from typing import Any
from typing import Iterable
from typing import List

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
            if isinstance(self.response.stream, Iterable):
                resp_iter1, resp_iter2 = tee(self.response.stream)
                self.response.stream = resp_iter1
                content = b"".join(resp_iter2)
                return content
            # checks ReadableIO protocol
            if hasattr(self.response.stream, "read"):
                data = self.response.stream.read()
                self.response.stream = BytesIO(data)
                return data
        assert isinstance(self.response.text, str)
        return self.response.text.encode("utf-8")

    @property
    def status_code(self) -> int:
        return self.response.status_code

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


class FalconAsgiOpenAPIResponse(FalconOpenAPIResponse):
    def __init__(self, response: Response, data: bytes):
        super().__init__(response)
        self._data = data

    @classmethod
    async def from_response(
        cls,
        response: Any,
    ) -> "FalconAsgiOpenAPIResponse":
        data = await cls._get_asgi_response_data(response)
        return cls(response, data=data)

    @classmethod
    async def _get_asgi_response_data(cls, response: Any) -> bytes:
        response_any = response
        stream = response_any.stream
        if stream is None:
            data = await response_any.render_body()
            if data is None:
                return b""
            assert isinstance(data, bytes)
            return data

        charset = getattr(response_any, "charset", None) or "utf-8"
        chunks: List[bytes] = []
        stream_any = stream

        if hasattr(stream_any, "__aiter__"):
            async for chunk in stream_any:
                if chunk is None:
                    break
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(charset)
                chunks.append(chunk)
        elif hasattr(stream_any, "read"):
            while True:
                chunk = stream_any.read()
                if inspect.isawaitable(chunk):
                    chunk = await chunk
                if not chunk:
                    break
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(charset)
                chunks.append(chunk)
        elif isinstance(stream_any, Iterable):
            response_iter1, response_iter2 = tee(stream_any)
            response_any.stream = response_iter1
            for chunk in response_iter2:
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(charset)
                chunks.append(chunk)
            return b"".join(chunks)

        response_any.stream = _AsyncChunksIterator(chunks)
        return b"".join(chunks)

    @property
    def data(self) -> bytes:
        return self._data


class _AsyncChunksIterator:
    def __init__(self, chunks: List[bytes]):
        self._chunks = chunks
        self._index = 0

    def __aiter__(self) -> "_AsyncChunksIterator":
        return self

    async def __anext__(self) -> bytes:
        if self._index >= len(self._chunks):
            raise StopAsyncIteration

        chunk = self._chunks[self._index]
        self._index += 1
        return chunk
