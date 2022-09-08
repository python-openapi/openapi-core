"""OpenAPI core contrib falcon responses module"""
from json import dumps
from typing import Any
from typing import Dict
from typing import Optional

from falcon.request import Request
from falcon.request import RequestOptions
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import RequestParameters


class FalconOpenAPIRequest:
    def __init__(
        self,
        request: Request,
        default_when_empty: Optional[Dict[Any, Any]] = None,
    ):
        self.request = request
        if default_when_empty is None:
            default_when_empty = {}
        self.default_when_empty = default_when_empty

        # Path gets deduced by path finder against spec
        self.parameters = RequestParameters(
            query=ImmutableMultiDict(list(self.request.params.items())),
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
    def body(self) -> Optional[str]:
        media = self.request.get_media(
            default_when_empty=self.default_when_empty
        )
        # Support falcon-jsonify.
        return dumps(getattr(self.request, "json", media))

    @property
    def mimetype(self) -> str:
        if self.request.content_type:
            assert isinstance(self.request.content_type, str)
            return self.request.content_type.partition(";")[0]

        assert isinstance(self.request.options, RequestOptions)
        assert isinstance(self.request.options.default_media_type, str)
        return self.request.options.default_media_type
