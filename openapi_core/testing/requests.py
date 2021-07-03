"""OpenAPI core testing requests module"""
from urllib.parse import urljoin

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


class MockRequestFactory:
    @classmethod
    def create(
        cls,
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
        path_pattern = path_pattern or path

        path = view_args or {}
        query = ImmutableMultiDict(args or {})
        header = Headers(headers or {})
        cookie = ImmutableMultiDict(cookies or {})
        parameters = RequestParameters(
            path=path,
            query=query,
            header=header,
            cookie=cookie,
        )
        method = method.lower()
        body = data or ""
        full_url_pattern = urljoin(host_url, path_pattern)
        return OpenAPIRequest(
            full_url_pattern=full_url_pattern,
            method=method,
            parameters=parameters,
            body=body,
            mimetype=mimetype,
        )
