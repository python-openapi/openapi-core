"""OpenAPI core contrib django requests module"""
import re
from typing import Dict
from urllib.parse import urljoin

from werkzeug.datastructures import ImmutableMultiDict, Headers

from openapi_core.contrib.django.compat import (
    get_request_headers, get_current_scheme_host,
)
from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)

# https://docs.djangoproject.com/en/2.2/topics/http/urls/
#
# Currently unsupported are :
#   - nested arguments, e.g.: ^comments/(?:page-(?P<page_number>\d+)/)?$
#   - unnamed regex groups, e.g.: ^articles/([0-9]{4})/$
#   - multiple named parameters between a single pair of slashes
#     e.g.: <page_slug>-<page_id>/edit/
#
# The regex matches everything, except a "/" until "<". Than only the name
# is exported, after which it matches ">" and everything until a "/".
PATH_PARAMETER_PATTERN = r'(?:[^\/]*?)<(?:(?:.*?:))*?(\w+)>(?:[^\/]*)'


class DjangoOpenAPIRequestFactory:

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    @classmethod
    def create(cls, request):
        if request.resolver_match is None:
            path_pattern = request.path
        else:
            route = cls.path_regex.sub(
                r'{\1}', request.resolver_match.route)
            # Delete start and end marker to allow concatenation.
            if route[:1] == "^":
                route = route[1:]
            if route[-1:] == "$":
                route = route[:-1]
            path_pattern = '/' + route

        request_headers = get_request_headers(request)
        params_path: Dict = request.resolver_match and \
            request.resolver_match.kwargs or {}
        params_query: ImmutableMultiDict = ImmutableMultiDict(request.GET)
        params_header: Headers = Headers(request_headers.items())
        params_cookie: ImmutableMultiDict = ImmutableMultiDict(
            dict(request.COOKIES))
        req_parameters = RequestParameters(
            path=params_path,
            query=params_query,
            header=params_header,
            cookie=params_cookie,
        )

        current_scheme_host = get_current_scheme_host(request)
        req_full_url_pattern: str = urljoin(current_scheme_host, path_pattern)
        req_method: str = request.method.lower()
        return OpenAPIRequest(
            full_url_pattern=req_full_url_pattern,
            method=req_method,
            parameters=req_parameters,
            body=request.body,
            mimetype=request.content_type,
        )
