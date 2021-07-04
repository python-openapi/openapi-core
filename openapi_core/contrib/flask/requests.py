"""OpenAPI core contrib flask requests module"""
import re
from urllib.parse import urljoin

from werkzeug.datastructures import Headers

from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters

# http://flask.pocoo.org/docs/1.0/quickstart/#variable-rules
PATH_PARAMETER_PATTERN = r"<(?:(?:string|int|float|path|uuid):)?(\w+)>"


class FlaskOpenAPIRequestFactory:

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    @classmethod
    def create(cls, request):
        method = request.method.lower()

        if request.url_rule is None:
            path_pattern = request.path
        else:
            path_pattern = cls.path_regex.sub(r"{\1}", request.url_rule.rule)

        header = Headers(request.headers)
        parameters = RequestParameters(
            path=request.view_args,
            query=request.args,
            header=header,
            cookie=request.cookies,
        )
        full_url_pattern = urljoin(request.host_url, path_pattern)
        return OpenAPIRequest(
            full_url_pattern=full_url_pattern,
            method=method,
            parameters=parameters,
            body=request.data,
            mimetype=request.mimetype,
        )
