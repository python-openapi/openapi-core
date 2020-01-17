"""OpenAPI core testing requests module"""
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)


class MockRequestFactory(object):

    @classmethod
    def create(
            cls, host_url, method, path, path_pattern=None, args=None,
            view_args=None, headers=None, cookies=None, data=None,
            mimetype='application/json'):
        parameters = RequestParameters(
            path=view_args or {},
            query=ImmutableMultiDict(args or []),
            header=headers or {},
            cookie=cookies or {},
        )
        path_pattern = path_pattern or path
        method = method.lower()
        body = data or ''
        return OpenAPIRequest(
            host_url=host_url,
            path=path,
            path_pattern=path_pattern,
            method=method,
            parameters=parameters,
            body=body,
            mimetype=mimetype,
        )
