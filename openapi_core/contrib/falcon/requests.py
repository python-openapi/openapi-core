"""OpenAPI core contrib falcon responses module"""
from json import dumps

from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import (
    OpenAPIRequest, RequestParameters,
)


class FalconOpenAPIRequestFactory:

    @classmethod
    def create(cls, request):
        """
        Create OpenAPIRequest from falcon Request and route params.
        """
        method = request.method.lower()

        # gets deduced by path finder against spec
        path = {}

        # Support falcon-jsonify.
        body = (
            dumps(request.json) if getattr(request, "json", None)
            else request.bounded_stream.read()
        )
        mimetype = request.options.default_media_type
        if request.content_type:
            mimetype = request.content_type.partition(";")[0]

        query = ImmutableMultiDict(request.params.items())
        parameters = RequestParameters(
            query=query,
            header=request.headers,
            cookie=request.cookies,
            path=path,
        )
        return OpenAPIRequest(
            full_url_pattern=request.url,
            method=method,
            parameters=parameters,
            body=body,
            mimetype=mimetype,
        )
