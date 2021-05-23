"""OpenAPI core testing requests module"""
from typing import Dict
from urllib.parse import urljoin

from werkzeug.datastructures import Headers, ImmutableMultiDict

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)


class MockRequestFactory:

    @classmethod
    def create(
            cls, host_url, method, path, path_pattern=None, args=None,
            view_args=None, headers=None, cookies=None, data=None,
            mimetype='application/json'):
        path_pattern = path_pattern or path

        params_path: Dict = view_args or {}
        params_query: ImmutableMultiDict = ImmutableMultiDict(args or {})
        params_header: Headers = Headers(headers or {})
        params_cookie: ImmutableMultiDict = ImmutableMultiDict(cookies or {})
        req_parameters = RequestParameters(
            path=params_path,
            query=params_query,
            header=params_header,
            cookie=params_cookie,
        )

        req_method: str = method.lower()
        req_body: str = data or ''
        req_full_url_pattern: str = urljoin(host_url, path_pattern)
        return OpenAPIRequest(
            full_url_pattern=req_full_url_pattern,
            method=req_method,
            parameters=req_parameters,
            body=req_body,
            mimetype=mimetype,
        )
