"""OpenAPI core contrib flask requests module"""
import re
from urllib.parse import urljoin

from werkzeug.datastructures import Headers

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)

# http://flask.pocoo.org/docs/1.0/quickstart/#variable-rules
PATH_PARAMETER_PATTERN = r'<(?:(?:string|int|float|path|uuid):)?(\w+)>'


class FlaskOpenAPIRequestFactory:

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    @classmethod
    def create(cls, request):
        params_header: Headers = Headers(request.headers)
        req_parameters = RequestParameters(
            path=request.view_args,
            query=request.args,
            header=params_header,
            cookie=request.cookies,
        )

        if request.url_rule is None:
            path_pattern = request.path
        else:
            path_pattern = cls.path_regex.sub(r'{\1}', request.url_rule.rule)
        req_full_url_pattern: str = urljoin(request.host_url, path_pattern)
        req_method: str = request.method.lower()
        return OpenAPIRequest(
            full_url_pattern=req_full_url_pattern,
            method=req_method,
            parameters=req_parameters,
            body=request.data,
            mimetype=request.mimetype,
        )
