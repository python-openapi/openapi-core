"""OpenAPI core testing mock module"""
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)
from openapi_core.validation.response.datatypes import OpenAPIResponse


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


class MockResponseFactory(object):

    @classmethod
    def create(cls, data, status_code=200, mimetype='application/json'):
        return OpenAPIResponse(
            data=data,
            status_code=status_code,
            mimetype=mimetype,
        )
