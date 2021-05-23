"""OpenAPI core contrib falcon responses module"""
from json import dumps

from werkzeug.datastructures import ImmutableMultiDict, Headers

from openapi_core.contrib.falcon.compat import get_request_media
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest, RequestParameters,
)


class FalconOpenAPIRequestFactory:

    @classmethod
    def create(cls, request, default_when_empty={}):
        """
        Create OpenAPIRequest from falcon Request and route params.
        """
        query = list(request.params.items())
        params_query: ImmutableMultiDict = ImmutableMultiDict(query)
        params_header: Headers = Headers(request.headers)
        # Path gets deduced by path finder against spec
        req_parameters = RequestParameters(
            query=params_query,
            header=params_header,
            cookie=request.cookies,
        )

        default = default_when_empty
        media = get_request_media(request, default=default)
        req_method: str = request.method.lower()
        # Support falcon-jsonify.
        req_body: str = (
            dumps(getattr(request, "json", media))
        )
        req_mimetype: str = request.options.default_media_type
        if request.content_type:
            req_mimetype = request.content_type.partition(";")[0]

        req_full_url_pattern: str = request.prefix + request.path
        return OpenAPIRequest(
            full_url_pattern=req_full_url_pattern,
            method=req_method,
            parameters=req_parameters,
            body=req_body,
            mimetype=req_mimetype,
        )
