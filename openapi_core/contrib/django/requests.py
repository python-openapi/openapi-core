"""OpenAPI core contrib django requests module"""
import re
from urllib.parse import urljoin

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters

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
PATH_PARAMETER_PATTERN = r"(?:[^\/]*?)<(?:(?:.*?:))*?(\w+)>(?:[^\/]*)"


class DjangoOpenAPIRequestFactory:

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    def create(self, request):
        return OpenAPIRequest(
            full_url_pattern=self._get_full_url_pattern(request),
            method=self._get_method(request),
            parameters=self._get_parameters(request),
            body=self._get_body(request),
            mimetype=self._get_mimetype(request),
        )

    def _get_parameters(self, request):
        return RequestParameters(
            path=self._get_path(request),
            query=self._get_query(request),
            header=self._get_header(request),
            cookie=self._get_cookie(request),
        )

    def _get_path(self, request):
        return request.resolver_match and request.resolver_match.kwargs or {}

    def _get_query(self, request):
        return ImmutableMultiDict(request.GET)

    def _get_header(self, request):
        return Headers(request.headers.items())

    def _get_cookie(self, request):
        return ImmutableMultiDict(dict(request.COOKIES))

    def _get_full_url_pattern(self, request):
        if request.resolver_match is None:
            path_pattern = request.path
        else:
            route = self.path_regex.sub(r"{\1}", request.resolver_match.route)
            # Delete start and end marker to allow concatenation.
            if route[:1] == "^":
                route = route[1:]
            if route[-1:] == "$":
                route = route[:-1]
            path_pattern = "/" + route

        current_scheme_host = request._current_scheme_host
        return urljoin(current_scheme_host, path_pattern)

    def _get_method(self, request):
        return request.method.lower()

    def _get_body(self, request):
        return request.body

    def _get_mimetype(self, request):
        return request.content_type
