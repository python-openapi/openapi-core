"""OpenAPI core contrib falcon responses module"""

from json import dumps
from typing import Any
from typing import Dict
from typing import Optional
from typing import cast

from falcon.request import Request
from falcon.request import RequestOptions
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.falcon.util import serialize_body
from openapi_core.contrib.falcon.util import unpack_params
from openapi_core.datatypes import RequestParameters

_BODY_NOT_SET = object()


class FalconOpenAPIRequest:
    def __init__(
        self,
        request: Request,
        default_when_empty: Optional[Dict[Any, Any]] = None,
    ):
        if not isinstance(request, Request):
            raise TypeError(f"'request' argument is not type of {Request}")
        self.request = request
        if default_when_empty is None:
            default_when_empty = {}
        self.default_when_empty = default_when_empty
        self._body: Any = _BODY_NOT_SET

        # Path gets deduced by path finder against spec
        self.parameters = RequestParameters(
            query=ImmutableMultiDict(unpack_params(self.request.params)),
            header=Headers(self.request.headers),
            cookie=self.request.cookies,
        )

    @property
    def host_url(self) -> str:
        assert isinstance(self.request.prefix, str)
        return self.request.prefix

    @property
    def path(self) -> str:
        assert isinstance(self.request.path, str)
        return self.request.path

    @property
    def method(self) -> str:
        assert isinstance(self.request.method, str)
        return self.request.method.lower()

    @property
    def body(self) -> Optional[bytes]:
        if self._body is not _BODY_NOT_SET:
            return cast(Optional[bytes], self._body)

        # Falcon doesn't store raw request stream.
        # That's why we need to revert deserialized data

        # Support falcon-jsonify.
        request_json = getattr(cast(Any, self.request), "json", None)
        if request_json is not None:
            self._body = dumps(request_json).encode("utf-8")
            return cast(Optional[bytes], self._body)

        media = self.request.get_media(
            default_when_empty=self.default_when_empty,
        )
        self._body = serialize_body(self.request, media, self.content_type)
        return cast(Optional[bytes], self._body)

    @property
    def content_type(self) -> str:
        if self.request.content_type:
            assert isinstance(self.request.content_type, str)
            return self.request.content_type

        assert isinstance(self.request.options, RequestOptions)
        assert isinstance(self.request.options.default_media_type, str)
        return self.request.options.default_media_type


class FalconAsgiOpenAPIRequest(FalconOpenAPIRequest):
    @classmethod
    async def from_request(
        cls,
        request: Request,
        default_when_empty: Optional[Dict[Any, Any]] = None,
    ) -> "FalconAsgiOpenAPIRequest":
        instance = cls(
            request,
            default_when_empty=default_when_empty,
        )
        media = await request.get_media(
            default_when_empty=instance.default_when_empty
        )
        instance._body = serialize_body(request, media, instance.content_type)
        return instance
