"""OpenAPI core contrib falcon responses module"""
from json import dumps

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import RequestParameters


class FalconOpenAPIRequest:
    def __init__(self, request, default_when_empty=None):
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
    def host_url(self):
        return self.request.prefix

    @property
    def path(self):
        return self.request.path

    @property
    def method(self):
        return self.request.method.lower()

    @property
    def body(self):
        media = self.request.get_media(
            default_when_empty=self.default_when_empty
        )
        # Support falcon-jsonify.
        return dumps(getattr(self.request, "json", media))

    @property
    def mimetype(self):
        if self.request.content_type:
            return self.request.content_type.partition(";")[0]
        return self.request.options.default_media_type
