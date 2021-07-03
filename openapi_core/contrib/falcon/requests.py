"""OpenAPI core contrib falcon responses module"""
from json import dumps

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


class FalconOpenAPIRequestFactory:
    def __init__(self, default_when_empty=None):
        if default_when_empty is None:
            default_when_empty = {}
        self.default_when_empty = default_when_empty

    def create(self, request):
        """
        Create OpenAPIRequest from falcon Request and route params.
        """
        method = request.method.lower()

        media = request.get_media(default_when_empty=self.default_when_empty)
        # Support falcon-jsonify.
        body = dumps(getattr(request, "json", media))
        mimetype = request.options.default_media_type
        if request.content_type:
            mimetype = request.content_type.partition(";")[0]

        query = ImmutableMultiDict(list(request.params.items()))
        header = Headers(request.headers)

        # Path gets deduced by path finder against spec
        parameters = RequestParameters(
            query=query,
            header=header,
            cookie=request.cookies,
        )
        url_pattern = request.prefix + request.path
        return OpenAPIRequest(
            full_url_pattern=url_pattern,
            method=method,
            parameters=parameters,
            body=body,
            mimetype=mimetype,
        )
