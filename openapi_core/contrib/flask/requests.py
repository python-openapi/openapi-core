"""OpenAPI core contrib flask requests module"""
import re
from urllib.parse import urljoin

from flask import Request
from werkzeug.datastructures import Headers

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)
from openapi_core.validation.request.factories import BaseOpenAPIRequestFactory


class FlaskOpenAPIRequestFactory(BaseOpenAPIRequestFactory):

    @classmethod
    def create(cls, request: Request) -> OpenAPIRequest:
        params_header: Headers = Headers(request.headers)
        # Path gets deduced by path finder against spec
        # request.view_args can contain coverted types (int, float, uuid)
        req_parameters = RequestParameters(
            query=request.args,
            header=params_header,
            cookie=request.cookies,
        )

        # We don' tprovide path parameters (see above) that why we can't use
        # path pattern of request.url_rule.rule
        req_full_url_pattern: str = urljoin(request.host_url, request.path)
        req_method: str = request.method.lower()
        return OpenAPIRequest(
            full_url_pattern=req_full_url_pattern,
            method=req_method,
            parameters=req_parameters,
            body=request.data,
            mimetype=request.mimetype,
        )
