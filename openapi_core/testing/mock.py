"""OpenAPI core wrappers module"""
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.wrappers.base import BaseOpenAPIRequest, BaseOpenAPIResponse


class MockRequest(BaseOpenAPIRequest):

    def __init__(
            self, host_url, method, path, path_pattern=None, args=None,
            view_args=None, headers=None, cookies=None, data=None,
            mimetype='application/json'):
        self.host_url = host_url
        self.path = path
        self.path_pattern = path_pattern or path
        self.method = method.lower()

        self.parameters = {
            'path': view_args or {},
            'query': ImmutableMultiDict(args or []),
            'header': headers or {},
            'cookie': cookies or {},
        }

        self.body = data or ''

        self.mimetype = mimetype


class MockResponse(BaseOpenAPIResponse):

    def __init__(self, data, status_code=200, mimetype='application/json'):
        self.data = data

        self.status_code = status_code
        self.mimetype = mimetype
