"""OpenAPI core contrib requests requests module"""
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)


class RequestsOpenAPIRequestFactory(object):

    @classmethod
    def create(cls, request):
        method = request.method.lower()

        cookie = request.cookies or {}

        # gets deduced by path finder against spec
        path = {}

        mimetype = request.headers.get('Accept') or \
            request.headers.get('Content-Type')
        parameters = RequestParameters(
            query=ImmutableMultiDict(request.params),
            header=request.headers,
            cookie=cookie,
            path=path,
        )
        return OpenAPIRequest(
            full_url_pattern=request.url,
            method=method,
            parameters=parameters,
            body=request.data,
            mimetype=mimetype,
        )
