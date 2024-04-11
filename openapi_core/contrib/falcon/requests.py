"""OpenAPI core contrib falcon responses module"""

import warnings
from json import dumps
from typing import Any
from typing import Dict
from typing import Optional

from falcon.request import Request
from falcon.request import RequestOptions
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.falcon.util import unpack_params
from openapi_core.datatypes import RequestParameters


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
        # Falcon doesn't store raw request stream.
        # That's why we need to revert deserialized data

        # Support falcon-jsonify.
        if hasattr(self.request, "json"):
            return dumps(self.request.json).encode("utf-8")

        media = self.request.get_media(
            default_when_empty=self.default_when_empty,
        )
        handler, _, _ = self.request.options.media_handlers._resolve(
            self.request.content_type, self.request.options.default_media_type
        )
        try:
            body = handler.serialize(
                media, content_type=self.request.content_type
            )
        # multipart form serialization is not supported
        except NotImplementedError:
            warnings.warn(
                f"body serialization for {self.request.content_type} not supported"
            )
            return None
        else:
            assert isinstance(body, bytes)
            return body

    @property
    def content_type(self) -> str:
        if self.request.content_type:
            assert isinstance(self.request.content_type, str)
            return self.request.content_type

        assert isinstance(self.request.options, RequestOptions)
        assert isinstance(self.request.options.default_media_type, str)
        return self.request.options.default_media_type
