"""OpenAPI core testing requests module"""

from typing import Any
from typing import Dict
from typing import Optional

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.datatypes import RequestParameters


class MockRequest:
    def __init__(
        self,
        host_url: str,
        method: str,
        path: str,
        path_pattern: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        view_args: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional[Dict[str, Any]] = None,
        data: Optional[bytes] = None,
        content_type: str = "application/json",
    ):
        self.host_url = host_url
        self.method = method.lower()
        self.path = path
        self.path_pattern = path_pattern
        self.args = args
        self.view_args = view_args
        self.headers = headers
        self.cookies = cookies
        self.body = data or b""
        self.content_type = content_type

        self.parameters = RequestParameters(
            path=self.view_args or {},
            query=ImmutableMultiDict(self.args or {}),
            header=Headers(self.headers or {}),
            cookie=ImmutableMultiDict(self.cookies or {}),
        )
