"""OpenAPI core testing requests module"""
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import RequestParameters


class MockRequest:
    def __init__(
        self,
        host_url,
        method,
        path,
        path_pattern=None,
        args=None,
        view_args=None,
        headers=None,
        cookies=None,
        data=None,
        mimetype="application/json",
    ):
        self.host_url = host_url
        self.method = method.lower()
        self.path = path
        self.path_pattern = path_pattern
        self.args = args
        self.view_args = view_args
        self.headers = headers
        self.cookies = cookies
        self.body = data or ""
        self.mimetype = mimetype

        self.parameters = RequestParameters(
            path=self.view_args or {},
            query=ImmutableMultiDict(self.args or {}),
            header=Headers(self.headers or {}),
            cookie=ImmutableMultiDict(self.cookies or {}),
        )
